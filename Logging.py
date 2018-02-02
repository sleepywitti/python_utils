"""
.. module:: Logging
   :synopsis: helpers for logging

.. moduleauthor:: C. Witt <cwitt@posteo.de>

- adds additional level for logging
- adds function wrapper to log every call of the function
"""

import logging

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"

LOGGING_DEVEL = logging.DEBUG - 1
logging.DEVEL = LOGGING_DEVEL
logging.addLevelName(LOGGING_DEVEL, 'DEVEL')
log = logging.getLogger(__name__)
log.setLevel(LOGGING_DEVEL)


def devel_logger_level(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(LOGGING_DEVEL):
        self._log(LOGGING_DEVEL, message, args, **kws)
logging.Logger.devel = devel_logger_level


def log_calls(fn):
    """ Wraps fn in a function named "inner" that writes the arguments and return value to log """

    def inner(*args, **kwargs):
        # Call the function with the received arguments and keyword arguments, storing the return value
        out = apply(fn, args, kwargs)

        # Write a line with the function name, its arguments, and its return value to the log file
        log.debug('%s called with args %s and kwargs %s, returning %s\n' % (fn.__name__,  args, kwargs, out))

        # Return the return value
        return out
    return inner
