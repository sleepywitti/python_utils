"""
.. module:: Logging
   :synopsis: helpers for logging

.. moduleauthor:: C. Witt <cwitt@posteo.de>

- method to get a system description string
- methods to get user data/config path that play nice with XDA
"""

import os
import platform

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"


def is_linux():
    return platform.system() == 'Linux'


def get_system_info() -> str:
    """
    :return: string with system information for debugging purpose
    """

    if is_linux():
        return 'Running on \'{host}\' ({dist}) using python{version} with {libc} at {sys} {release} {arch}'.format(
            version=platform.python_version(), sys=platform.system(), release=platform.release(),
            arch=platform.architecture()[0], host=platform.node(), dist=' '.join(platform.linux_distribution()).strip(),
            libc=''.join(platform.libc_ver()))
    else:
        return 'Running on \'{host}\' using python{version} at {sys} {release} {arch}'.format(
            version=platform.python_version(), sys=platform.system(), release=platform.release(),
            arch=platform.architecture()[0], host=platform.node())


def get_user_data_path(appname: str) -> str:
    """
    :return: user data path
    """
    system = platform.system()
    if system == 'Windows':
        # C:\Users\<username>\AppData\Local\<AppName>
        path = os.getenv('LOCALAPPDATA', os.path.expanduser('~/AppData/Local/'))
    elif system == 'Darwin':  # ~/Library/Application Support/<AppName>
        path = os.path.join(os.path.expanduser('~/Library/Application Support/'), __app__)
    else:  # ~/.local/share/<AppName>
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser("~/.local/share"))
    path = os.path.join(path, appname)
    return path


def get_user_config_path(appname: str) -> str:
    """
    :return: user config path
    """
    system = platform.system()
    if system == 'Windows':
        # C:\Users\<username>\AppData\Local\<AppName>
        data_path = os.getenv('LOCALAPPDATA', os.path.expanduser('~/AppData/Local/'))
    elif system == 'Darwin':  # ~/Library/Preferences/<AppName>
        data_path = os.path.join(os.path.expanduser('~/Library/Preferences/'), __app__)
    else:  # ~/.config/<AppName>
        data_path = os.getenv('XDG_CONFIG_HOME', os.path.expanduser("~/.config"))
    data_path = os.path.join(data_path, appname)
    return data_path
