"""
.. module:: Settings
   :synopsis: extension of configparser

.. moduleauthor:: C. Witt <cwitt@posteo.de>

- adds fallback
- adds default settings
- adds ignored sections that will not be written in file
"""

import logging
log = logging.getLogger(__name__)

import configparser

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"

# noinspection PyProtectedMember
_UNSET = configparser._UNSET


class Settings(configparser.ConfigParser):
    """extended ConfigParser with default and ignored section support"""

    def __init__(self, defaults=None, ignored_sections=list(), **keywords):
        super().__init__(allow_no_value=False, **keywords)
        if defaults:
            self.read_dict(defaults)
        self.defaults = defaults
        self.fallback = dict()
        self.ignored_sections = list(ignored_sections)

    def __copy__(self):
        settings = Settings(defaults=self.defaults, ignored_sections=self.ignored_sections)
        for section in self.sections():
            for option in self.options(section):
                settings.set(section, option, self.getstr(section, option))
        return settings

    def __str__(self):
        return ''.join([''.join(['[{0}]\n'.format(sec) + ''.join(
            ['  {0} = {1}\n'.format(var, val) for var, val in self.items(sec)])]) for sec in self.sections()])

    def copy(self):
        return self.__copy__()

    def remember_fallback(self, section, option, fallback):
        if id(fallback) == id(_UNSET):
            return
        if section not in self.fallback:
            self.fallback[section] = dict()
        if option not in self.fallback[section]:
            self.fallback[section][option] = fallback
        elif self.fallback[section][option] != fallback:
            log.debug('different fallback values detected for {0}{1} having {2} != {3}'.format(
                section, option, self.fallback[section][option], fallback))

    # noinspection PyMethodOverriding,PyShadowingBuiltins
    def getstr(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        """
        :type section: str
        :type option: str
        :type raw: bool
        :type vars: dict
        :type fallback: str
        :rtype : str
        """
        self.remember_fallback(section, option, fallback)
        return super().get(section, option, fallback=fallback)

    # noinspection PyMethodOverriding,PyShadowingBuiltins
    def getboolean(self, section, option, raw=False, vars=None, fallback=_UNSET):
        """
        :type section: str
        :type option: str
        :type raw: bool
        :type vars: dict
        :type fallback: bool
        :rtype : bool
        """
        self.remember_fallback(section, option, fallback)
        return super().getboolean(section, option, fallback=fallback)

    # noinspection PyMethodOverriding,PyShadowingBuiltins
    def getfloat(self, section, option, raw=False, vars=None, fallback=_UNSET):
        """
        :type section: str
        :type option: str
        :type raw: bool
        :type vars: dict
        :type fallback: float
        :rtype : float
        """
        self.remember_fallback(section, option, fallback)
        return super().getfloat(section, option, fallback=fallback)

    # noinspection PyMethodOverriding,PyShadowingBuiltins
    def getint(self, section, option, raw=False, vars=None, fallback=_UNSET):
        """
        :type section: str
        :type option: str
        :type raw: bool
        :type vars: dict
        :type fallback: int
        :rtype : int
        """
        self.remember_fallback(section, option, fallback)
        return super().getint(section, option, fallback=fallback)

    def set(self, section, option, value=None):
        """ Set an option
        :type section: str
        :type option: str
        :type value: str
        """
        if section not in self.sections():
            self.add_section(section)
        if not isinstance(value, str):
            value = str(value)
        super().set(section, option, value)

    def write(self, fp, space_around_delimiters=True, skip_defaults=True):
        backup = dict()
        for section in self.ignored_sections:
            if self.has_section(section):
                backup[section] = self.items(section)
                self.remove_section(section)

        if skip_defaults:
            sections = self.sections()
            for section in sections:
                if section in self.defaults:
                    for item, value in self.items(section):
                        if item in self.defaults[section] and value == str(self.defaults[section][item]):
                            self.remove_option(section, item)
                    if len(self.items(section)) == 0:
                        self.remove_section(section)

        with open(fp, 'w') as configfile:
            super().write(configfile, space_around_delimiters)

        for section, items in backup.items():
            self.add_section(section)
            for option, value in items:
                self.set(section, option, value)

    def save(self, path):
        with open(path, 'w') as file:
            self.write(file)
