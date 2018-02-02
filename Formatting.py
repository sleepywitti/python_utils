"""
.. module:: Formatting
   :synopsis: helpers for formatting

.. moduleauthor:: C. Witt <cwitt@posteo.de>

- method for generating pretty tables
- method of indent text
- method for colorful and indented logging
"""

import logging
import textwrap
import sys
import shutil
from typing import List

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"

terminal_size = shutil.get_terminal_size(fallback=(80, 20))


def pretty_table(rows: List[List[str]], indent: int=0, left_align: bool=False) -> str:
    """ indents message_b by using the length of message_a """
    def just(s, w, l):
        return str(s).ljust(w) if l else str(s).rjust(w)

    columns = [[rows[rowIdx][colIdx] for rowIdx in range(len(rows))] for colIdx in range(len(rows[0]))]
    max_widths = [max([len(str(item)) for item in column]) for column in columns]
    output = [' | '.join([just(cell, max_widths[col], left_align) for col, cell in enumerate(row)]) for row in rows]
    output.insert(1, '-|-'.join(['-' * width for width in max_widths]))
    if indent:
        for i in range(len(output)):
            output[i] = ' ' * indent + output[i]
    return '\n'.join(output)


def indent_format(message_a: str, message_b: str, wrap: int=terminal_size.columns) -> str:
    """ indents message_b by using the length of message_a """
    if (len(message_a) + 20) > wrap:
        return message_a + message_b
    else:
        split_message = message_b.splitlines()
        wrapped_lines = '\n'.join([textwrap.fill(line, replace_whitespace=False, width=wrap - len(message_a))
                                   for line in split_message]).splitlines()
        indent = '\n' + ' ' * len(message_a)
        return message_a + indent.join(wrapped_lines)


class IndentFormatter(logging.Formatter):
    """ Formatter Class to use colored, bold or italic text inside console output """
    sc = '~'  # special_character
    formats = {sc * 2: '\033[0m', sc + 'b': '\033[1m', sc + 'i': '\033[3m',
               sc + 'k': '\033[0;37m', sc + 'r': '\033[0;31m', sc + 'g': '\033[0;32m', sc + 'y': '\033[0;33m',
               sc + 'a': '\033[0;34m', sc + 'm': '\033[0;35m', sc + 'c': '\033[0;36m', sc + 'w': '\033[0;30m'}
    colors = {'WARNING': 'g', 'INFO': 'a', 'DEBUG': 'k', 'DEVEL': 'k', 'CRITICAL': 'r', 'ERROR': 'm'}

    def __init__(self, fmt: str, datefmt: str=None, style: str='%', wrap: int=None, use_color: bool=False):
        """ initiates text
        @param fmt: log format
        @param datefmt: log date format
        @param style: log style
        @param wrap: text width for wrapping
        @param use_color: use colored output
        """
        fmt = fmt.replace('%(indent)', self.sc + 'n')  # replaces indent indicator to #n
        logging.Formatter.__init__(self, fmt, datefmt, style)
        self.wrap = wrap if wrap else terminal_size.columns  # set wrapping length
        self.use_color = use_color if sys.platform == 'linux' else False

    @staticmethod
    def color(string, use_color: bool):
        # replaces color indicators
        if use_color:
            for key, value in IndentFormatter.formats.items():
                string = string.replace(key, value)
        else:
            for key, value in IndentFormatter.formats.items():
                string = string.replace(key, '')
        return string

    def format(self, record: logging.LogRecord):
        """ formats string
        @param record: string to format
        """
        message = logging.Formatter.format(self, record)

        # process indention
        separated_msg = message.split(self.sc + 'n', 2)  # split by
        if len(separated_msg) == 2:
            indent_length = len(self.color(separated_msg[0][:], False))  # calculate length to %(indent)
            if self.wrap:
                string = indent_format(separated_msg[0], separated_msg[1], self.wrap)
            else:  # no wrap
                string = separated_msg[0] + ('\n' + ' ' * indent_length).join(separated_msg[1].split('\n'))

        else:  # no indention
            string = message

        # process coloring
        if self.use_color and record.levelname in self.colors:
            string = '{s}{color}{msg}{s}{s}'.format(color=self.colors[record.levelname], msg=string, s=self.sc)

        string = self.color(string, self.use_color)

        return string
