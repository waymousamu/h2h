'''
=====================
`logger` module
=====================

A simplified interface to the standard library's logging module.

Summary
-------

Two handlers are attached to the root logger, one logs to a file and the other
logs to the console.  Log levels of the two handlers can be set independently
by calling `setloglevel()` and '`setecholevel()`.  Logging can be enabled with
`enable()` and disabled with `disable()`.

The file logger is in fact optional, and is only enabled if `start()`
is called with either a `logdir` parameter or a `logfile` parameter.
In the case where you only want logging to the console (stdout), then it
It is not necessary to call *start()* explicitly, it will be called behind the
scenes once any of the logging statements are invoked.

All logging statements:
-----------------------

    * debug
    * info
    * warning
    * error
    * critical
    * exception
    * divider

Usage
-----

Basic usage:

.. sourcecode:: python

    >>> debug("A debug statement.")
    DEBUG    A debug statement.
    >>> info("Some info.")
    INFO     Some info.
    >>> warning("A warning")
    WARNING  A warning
    >>> error("A bad thing.")
    ERROR    A bad thing.

Raise the logging level for the console logger:

.. sourcecode:: python

    >>> setecholevel(logging.ERROR)
    >>> info("Some info.")
    >>> warning("A warning")
    >>> error("A bad thing.")
    ERROR    A bad thing.

And lower it again:

.. sourcecode:: python

    >>> setecholevel(logging.INFO)
    >>> info("Some info.")
    INFO     Some info.
    >>> warning("A warning")
    WARNING  A warning
    >>> end()
    INFO     End logging.

Logging messages may also be sent to a file

.. sourcecode:: python

    >>> import tempfile
    >>> fp, tmp = tempfile.mkstemp()
    >>> log = start(logfile=tmp) #doctest:+ELLIPSIS
    >>> tmp == log
    True
    >>> info("Some info.")
    INFO     Some info.
    >>> warning("A warning")
    WARNING  A warning

Temporarily disable all logging.

.. sourcecode:: python

    >>> disable()
    >>> debug('Debugging')
    >>> info("Some info.")
    >>> warning("A warning")
    >>> error("A bad thing.")
    >>> critical("Even worser.")

And re-enable.

.. sourcecode:: python

    >>> enable()
    >>> info("Some info.")
    INFO     Some info.
    >>> debug('Debugging')
    >>> setecholevel(logging.DEBUG)
    >>> debug('Debugging')
    DEBUG    Debugging
    >>> end()
    INFO     End logging.

Here we verify that the log file exists and is non-empty:
(`end` should close all open file-handles, but it doesn't
here, so have to do it with `os.close()` - related to tempfile.mkstemp perhaps).

.. sourcecode:: python

    >>> os.close(fp)  
    >>> os.path.exists(log)
    True
    >>> os.stat(log).st_size > 0
    True

and tidy up:

.. sourcecode:: python

    >>> os.remove(log)

'''

__docformat__ = "restructuredtext en"
__author__ = "Gerard Flanagan <gerard.flanagan@euroclear.com>"

import os
import logging
from datetime import datetime
import functools

__all__ = [
        'step','disable_step',
        'start', 'end','debug', 'info', 'warning', 'critical',
        'error', 'exception', 'event', 'divider', 'mklogname',
        'setloglevel', 'setecholevel', 'enable', 'disable'
        ]

__doc_all__ = __all__

LOGNAME_FORMAT = "%Y%m%d-%H%M%S.log"
#LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_FORMAT = '%(asctime)s [%(user)s@%(clientip)s] %(levelname)-8s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
LOG_LEVEL = logging.DEBUG
ECHO_FORMAT = '%(levelname)-8s %(message)s'
ECHO_LEVEL = logging.DEBUG

def getuser():
    try:
        import win32api
        usr = win32api.GetUserName()
    except ImportError:
        import getpass
        usr = getpass.getuser()
    return usr or 'unknown'

def getclientip():
    import socket
    try:
        return socket.gethostbyaddr(socket.gethostname())[2][0]
    except:
        return 'unknown'

KWARGS = {}

def mklogname(prefix=''):
    '''
    Generate a timestamped log file name. Eg. 20071210_140934.log
    '''

    return prefix + datetime.now().strftime(LOGNAME_FORMAT)

def start(logfile=None, logdir=None, logfileprefix='', level=ECHO_LEVEL):
    '''
    Start logging 

    :param logfile: The name of a file to log to.
    :param logdir: If `logfile` is not specified create one here.
    :param logfileprefix: Prefix to add to log file names.
    :param level: The logging level, by default DEBUG

    :return: The absolute path of the logfile
    '''
    import sys
    global KWARGS
    KWARGS['user'] = getuser()
    KWARGS['clientip'] = getclientip()
    root = logging.getLogger()
    root.setLevel(level)
    if len(root.handlers) == 0:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(ECHO_LEVEL)
        formatter = logging.Formatter(ECHO_FORMAT, DATE_FORMAT)
        console.setFormatter(formatter)
        root.addHandler(console)
    if logdir or logfile:
        logfile = os.path.abspath(logfile or \
                            os.path.join(logdir, mklogname(logfileprefix)))
        logdir = os.path.dirname(logfile)
        if not os.path.exists(logdir):
            try:
                os.makedirs(logdir)
            except:
                raise Exception("Error creating log directory: %s" % logdir)
        hdlr = logging.FileHandler(logfile, 'a')
        hdlr.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        hdlr.setFormatter(formatter)
        root.addHandler(hdlr)
    return logfile

def end():
    '''
    End logging, closing all file handles.

    :return: None
    '''
    info('End logging.')
    logging.shutdown()

def setloglevel(level):
    '''
    Set the logging level for the file logger.
    '''
    if len(logging.root.handlers) > 1:
        global LOG_LEVEL
        LOG_LEVEL = level
        logging.root.handlers[1].setLevel(level)


def setecholevel(level):
    '''
    Set the logging level for the console logger.
    '''
    if len(logging.root.handlers) > 0:
        global ECHO_LEVEL
        ECHO_LEVEL = level
        logging.root.handlers[0].setLevel(level)

def disable():
    '''
    Disable logging on all handlers.
    '''
    logging.root.manager.disable = logging.CRITICAL + 10

def enable():
    '''
    Renable logging if it has been disabled.
    '''
    logging.root.manager.disable = min(ECHO_LEVEL, LOG_LEVEL) - 10


def _start(func):
    def wrapper(msg, *args):
        if len(logging.root.handlers) == 0:
            start()
        func(msg, *args)
    functools.update_wrapper(wrapper, func)
    return wrapper

STEP = 0
def step(func):
    '''
    A function decorator. This will log a step number such as 0005, then
    call the decorated function, then ouput an 'end step' marker, eg. Done.
    '''
    def wrapper(*args, **kwargs):
        global STEP
        STEP += 1
        id = "%04d    " % STEP
        divider()
        info("%s%s" % (id, func.__name__))
        divider()
        ret = func(*args, **kwargs)
        info("Done.(%s)" % id.strip())
        return ret
    functools.update_wrapper(wrapper, func)
    return wrapper

@_start
def debug(msg, *args):
    '''
    Logs a message with level 10 (DEBUG) to the root logger.

    :param msg: Message to be written

    :return: None
    '''
    logging.debug(msg, extra=KWARGS)

@_start
def info(msg, *args):
    '''
    Logs a message with level 20 (INFO) to the root logger.

    :param msg: Message to be written

    :return: None
    '''
    logging.info(msg, extra=KWARGS)

@_start
def warning(msg, *args):
    '''
    Logs a message with level 30 (WARNING) to the root logger.

    :param msg: Message to be written

    :return: None
    '''
    logging.warning(msg, extra=KWARGS)

@_start
def error(msg, *args):
    '''
    Logs a message with level 40 (ERROR) to the root logger.

    :param msg: Message to be written

    :return: None
    '''
    logging.error(msg, extra=KWARGS)

@_start
def critical(msg, *args):
    '''
    Logs a message with level 50 (CRITICAL) to the root logger.

    :param msg: Message to be written

    :return: None
    '''
    logging.critical(msg, extra=KWARGS)

@_start
def exception(msg, *args):
    '''
    Logs a message with level 40 (ERROR) to the root logger, and
    adds exception information to the log.  This function should
    only be called from within an exception handler.

    :param msg: Message to be written

    :return: None
    '''
    logging.exception(msg, *args)

def divider(char=':'):
    '''
    Create a dividing line in the log output.

    :param char: The character of which the dividing line will be composed, by default a ':'.
    '''
    info(char*70)

@_start
def event(lvl, msg, *args):
    '''
    Logs a message with the specified level to the root logger.
    '''
    logging.log(lvl, msg, extra=KWARGS)

if __name__ == '__main__':
    import doctest
    doctest.testmod()


