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

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"

terminal_size = shutil.get_terminal_size(fallback=(80, 20))


def pretty_table(rows, indent=0, leftAlign=False):
    columns = [[rows[rowIdx][colIdx] for rowIdx in range(len(rows))] for colIdx in range(len(rows[0]))]
    max_widths = [max([len(str(item)) for item in column]) for column in columns]
    just = lambda s, w: str(s).ljust(w) if leftAlign else lambda s, w: str(s).rjust(w)
    output = [' | '.join([just(cell, max_widths[col]) for col, cell in enumerate(row)]) for row in rows]
    output.insert(1, '-|-'.join(['-' * width for width in max_widths]))
    if indent:
        for i in range(len(output)):
            output[i] = ' ' * indent + output[i]
    return '\n'.join(output)


def indent_format(message_a, message_b):
    if (len(message_a) + 20) > terminal_size.columns:
        return message_a + message_b
    else:
        return textwrap.fill(message_b, width=terminal_size.columns, initial_indent=message_a,
                             subsequent_indent=' ' * len(message_a))


class IndentFormatter(logging.Formatter):
    """ Formatter Class to use colored, bold or italic text inside console output """
    sc = '~'  # special_character
    formats = {sc * 2: '\033[0m', sc + 'b': '\033[1m', sc + 'i': '\033[3m',
               sc + 'k': '\033[0;37m', sc + 'r': '\033[0;31m', sc + 'g': '\033[0;32m', sc + 'y': '\033[0;33m',
               sc + 'a': '\033[0;34m', sc + 'm': '\033[0;35m', sc + 'c': '\033[0;36m', sc + 'w': '\033[0;30m'}
    colors = {'WARNING': 'g', 'INFO': 'a', 'DEBUG': 'k', 'DEVEL': 'k', 'CRITICAL': 'r', 'ERROR': 'm'}

    def __init__(self, fmt, datefmt=None, style='%', wrap=None, useColor=False):
        """ initiates text
        @param fmt: log format
        @param datefmt: log date format
        @param style: log style
        @param wrap: text width for wrapping
        @param useColor: use colored output
        """
        fmt = fmt.replace('%(indent)', self.sc + 'n')  # replaces indent indicator to #n
        logging.Formatter.__init__(self, fmt, datefmt, style)
        self.wrap = wrap if wrap is not None else terminal_size.columns  # set wrapping length
        self.useColor = useColor if sys.platform == 'linux' else False

    @staticmethod
    def color(string, useColor):
        # replaces color indicators
        if useColor:
            for key, value in IndentFormatter.formats.items():
                string = string.replace(key, value)
        else:
            for key, value in IndentFormatter.formats.items():
                string = string.replace(key, '')
        return string

    def format(self, record):
        """ formats string
        @param record: string to format
        """
        message = logging.Formatter.format(self, record)

        # process indention
        separatedMsg = message.split(self.sc + 'n', 2)  # split by
        if len(separatedMsg) == 2:
            indentLength = len(self.color(separatedMsg[0][:], False))  # calculate length to %(indent)
            if self.wrap:
                string = textwrap.fill(separatedMsg[1],  # process first line
                                       replace_whitespace=False,  # leave whitespaces
                                       width=self.wrap,  # calculate width for wrapping
                                       initial_indent=separatedMsg[0],  # append first line pretext
                                       subsequent_indent=' ' * indentLength)
            else:  # no wrap
                string = separatedMsg[0] + ('\n' + ' ' * indentLength).join(separatedMsg[1].split('\n'))

        else:  # no indention
            string = message

        # process coloring
        if self.useColor and record.levelname in self.colors:
            string = '{s}{color}{msg}{s}{s}'.format(color=self.colors[record.levelname], msg=string, s=self.sc)

        string = self.color(string, self.useColor)

        return string
