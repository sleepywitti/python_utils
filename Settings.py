"""
.. module:: Settings
   :synopsis: extension of configparser

.. moduleauthor:: C. Witt <cwitt@posteo.de>

additions:
- raises errors when used fallback differs
- adds defaults that are ignored when saving
- adds ignored sections that will not be written in file
- adds temporary (not saved) settings
"""

import configparser
from typing import Union

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"

# noinspection PyProtectedMember
_UNSET = configparser._UNSET


# noinspection PyMethodOverriding,PyShadowingBuiltins
class Settings(configparser.ConfigParser):
    """extended ConfigParser with default and ignored section support"""

    def __init__(self, defaults: dict=None, ignored_sections: Union[list, str]=list(), **keywords):
        super().__init__(allow_no_value=False, **keywords)
        if defaults:
            self.read_dict(defaults)
        self.defaults = defaults
        self.original = dict()
        self.fallback = dict()
        self.ignored_sections = list(ignored_sections)

    def __copy__(self):
        settings = Settings(defaults=self.defaults, ignored_sections=self.ignored_sections)
        self.original = self.original
        self.fallback = self.fallback
        for section in self.sections():
            for option in self.options(section):
                settings.set(section, option, self.getstr(section, option))
        return settings

    def __str__(self):
        return ''.join([''.join(['[{0}]\n'.format(sec) + ''.join(
            ['  {0} = {1}\n'.format(var, val) for var, val in self.items(sec)])]) for sec in self.sections()])

    def copy(self):
        return self.__copy__()

    def remember_fallback(self, section: str, option: str, fallback: Union[str, bool, float, int]):
        if id(fallback) == id(_UNSET):
            return
        if section not in self.fallback:
            self.fallback[section] = dict()
        if option not in self.fallback[section]:
            self.fallback[section][option] = fallback
        elif self.fallback[section][option] != fallback:
            raise ValueError('different fallback values detected for {0}{1} having {2} != {3}'.format(
                section, option, self.fallback[section][option], fallback))

    def remember_original(self, section: str, option: str):
        if section not in self.original:
            self.original[section] = dict()
        if option not in self.original[section]:
            self.original[section][option] = super().get(section, option, fallback='')

    def getstr(self, section: str, option: str, raw: bool=False, vars: dict=None, fallback: str=_UNSET) -> str:
        """ returns option's value as string """
        self.remember_fallback(section, option, fallback)
        return super().get(section, option, raw=raw, vars=vars, fallback=fallback)

    def getboolean(self, section: str, option: str, raw: bool=False, vars: dict=None, fallback: bool=_UNSET) -> bool:
        """ returns option's value as boolean """
        self.remember_fallback(section, option, fallback)
        return super().getboolean(section, option, raw=raw, vars=vars, fallback=fallback)

    def getfloat(self, section: str, option: str, raw: bool=False, vars: dict=None, fallback: float=_UNSET) -> float:
        """ returns option's value as float """
        self.remember_fallback(section, option, fallback)
        return super().getfloat(section, option, raw=raw, vars=vars, fallback=fallback)

    def getint(self, section: str, option: str, raw: bool=False, vars: dict=None, fallback: int=_UNSET) -> int:
        """ returns option's value as int """
        self.remember_fallback(section, option, fallback)
        return super().getint(section, option, raw=raw, vars=vars, fallback=fallback)

    def set(self, section: str, option: str, value: Union[str, bool, float, int]=None, temporary: bool=False) -> None:
        """ Set an option """
        if section not in self.sections():
            self.add_section(section)
        if not isinstance(value, str):
            value = str(value)
        if temporary:
            self.remember_original(section, option)
        super().set(section, option, value)

    def write(self, fp: str, space_around_delimiters: bool=True, skip_defaults: bool=True,
              skip_tamporary: bool=True) -> None:
        backup = dict()
        temporary_backup = dict()
        if skip_tamporary:
            for section in self.original:
                temporary_backup[section] = dict()
                for option, value in self.original[section].items():
                    temporary_backup[section][option] = self.get(section, option)
                    self.set(section, option, value)

        for section in self.ignored_sections:
            if self.has_section(section):
                backup[section] = self.items(section)
                self.remove_section(section)

        if skip_defaults:
            sections = self.sections()
            for section in sections:
                if section in self.defaults:
                    for option, value in self.items(section):
                        if option in self.defaults[section] and value == str(self.defaults[section][option]):
                            self.remove_option(section, option)
                    if len(self.items(section)) == 0:
                        self.remove_section(section)

        if isinstance(fp, str):
            with open(fp, 'w') as configfile:
                super().write(configfile, space_around_delimiters)
        else:
            raise ValueError('type = {}'.format(type(fp)))

        for section, items in backup.items():
            self.add_section(section)
            for option, value in items:
                self.set(section, option, value)

        for section in temporary_backup.keys():
            if section not in self.sections():
                self.add_section(section)
            for option, value in temporary_backup[section].items():
                self.set(section, option, value, temporary=True)
