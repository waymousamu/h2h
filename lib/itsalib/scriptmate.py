
from __future__ import with_statement

import threading
import os, sys
import optparse
import inspect
from itsalib import logger as log
from itsalib.deploytools import mktempfile
__all__ = [
        'SCRIPT', 'ARGS', 'KWARGS', 'logstart', 
        'CommonOptionParser', 'CommonOptionWithGuiParser', 'mkoption',
        'mainmethod',
        ]

OPTCONFIG = "config"
OPTCONFIGFILE = "configfile"
OPTALIASES = "aliases"
OPTALIASESFILE = "aliasfile"
OPTLOGFILE = "logfile"
OPTLOGDIR = "logdir"
OPTLOGPREFIX = "logprefix"
OPTGUI = 'gui'
COMMONOPTNAMES = [OPTCONFIG, OPTCONFIGFILE, OPTLOGFILE, OPTLOGDIR, OPTLOGPREFIX]
HELPCONFIG = "A ConfigObj style configuration file."
HELPLOGFILE = """If LOGDIR and LOGPREFIX are not given, you can supply a file
name."""
HELPLOGDIR = "A directory in which to create a time-stamped log file."
HELPLOGPREFIX = "Add a prefix to the log file created in LOGDIR"
ERRMSGLOGDIRANDFILE = "Specify either a log file or a log directory. Not both."

def get_main_dir():
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0]) 

APPDIR = os.path.abspath(get_main_dir())
DEFAULTLOGDIR = os.path.join(APPDIR, 'log')

def _getargs(allargs):
    args = []
    kwargs = {}
    key = None
    while allargs:
        arg = allargs.pop(0)
        if arg.startswith('-'):
            arg = arg[1:]
            if arg.startswith('-'):
                arg = arg[1:]
            else:
                parts = arg.split('=', 1)
                key = parts[0]
                if len(parts) > 1:
                    arg = parts[1]
            if not allargs or allargs[0].startswith('-'):
                allargs.insert(0, 'yes')
            continue
        if key is None:
            args.append(arg)
        else:
            kwargs[key] = arg
            key = None
    return args, kwargs

SCRIPT = sys.argv[0]
ARGS, KWARGS = _getargs(sys.argv[1:])

def logstart(logfile=None, logdir=None, logprefix='itsa-'):
    '''
    Initialise file and console loggers.

    * logdir: The directory where the timestamped log file will be saved.
    * logfile: If `logdir` is not specified, log to this file.

    :return: The log file path.
    '''
    if not (logdir or logfile):
        #logdir = DEFAULTLOGDIR
        logfile = mktempfile(prefix=logprefix, suffix='.log').name
    logfile = log.start(logfile, logdir, logprefix)
    log.divider()
    if logfile:
        log.info("Started logger. Logging to file: '%s'" % logfile)
    else:
        log.info("Started logger. A log file or directory was not specified.")
    return logfile

def _on_config(option, key, val, parser, configspec=None):
    from itsalib.util.configobj import ConfigObj
    config = ConfigObj(val, configspec=configspec, write_empty_values=True)
    if configspec is not None:
        from itsalib.util.validate import Validator
        vdt = Validator()
        result = config.validate(vdt)
        if result is not True:
            msg = 'Validation Errors.\n\n'
            for item in configobj.flatten_errors(config, result):
                msg += ' %s:%s:%s\n' % item
            msg += '\n%s\n' % configspec
            raise optparse.OptionValueError(msg)
    setattr(parser.values, OPTCONFIG, config)
    setattr(parser.values, OPTCONFIGFILE, val)

def _on_logfile(option, key, val, parser):
    if getattr(parser.values, OPTLOGDIR):
        raise optparse.OptionValueError(ERRMSGLOGDIRANDFILE)
    setattr(parser.values, OPTLOGFILE, val)

def _on_logdir(option, key, val, parser):
    if getattr(parser.values, OPTLOGFILE):
        raise optparse.OptionValueError(ERRMSGLOGDIRANDFILE)
    setattr(parser.values, OPTLOGDIR, val)

def _on_alias(option, key, val, parser):
    from itsalib.util import xlrd
    pass
    
mkoption = optparse.make_option

COMMONOPTS = [
        #mkoption("-a", "--%s" % OPTALIASES, type="string", action="callback",
        #                callback=_on_alias, default=None, help=HELPALIAS),
        mkoption("-d", "--%s" % OPTLOGDIR, type="string", action="callback",
                        callback=_on_logdir, default=None, help=HELPLOGDIR),
        mkoption("-p", "--%s" % OPTLOGPREFIX, type="string", action="store",
                        dest=OPTLOGPREFIX, default='', help=HELPLOGPREFIX),
        mkoption("-l", "--%s" % OPTLOGFILE, type="string", action="callback",
                        callback=_on_logfile, default=None, help=HELPLOGFILE),
                ]

class CommonOptionParser(optparse.OptionParser):

    _opts = COMMONOPTS
    def __init__(self, prog=None, desc=None, usage=None,
                        configspec=None, noconfig=False, **kw):
        optparse.OptionParser.__init__(self, prog=prog, description=desc,
                                            usage=usage, **kw)
        if not noconfig:
            confopt = mkoption("-c", "--%s" % OPTCONFIG, type="string",
                            action="callback", callback=_on_config,
                            help=HELPCONFIG, callback_args=(configspec,),
                            default=None)
            self.add_option(confopt)
        for opt in self._opts:
            self.add_option(opt)

GUIOPT = mkoption("-g", "--%s" % OPTGUI,
                  action="store_true", dest="gui", default=False,
                  help="launch gui version.")

class CommonWithGuiOptionParser(CommonOptionParser):

    _opts = CommonOptionParser._opts + [GUIOPT]


class ScriptContext(object):
    pass

class mainmethod(object):

    _parser = None
    kwargs = {'appdir': APPDIR}
    args =()

    def _getparser(self):
        if self._parser is None:
            self._parser = CommonOptionParser()
        return self._parser
    parser = property(_getparser)

    def __new__(cls, *args, **kw):
        obj = super(mainmethod, cls).__new__(cls, *args, **kw)
        if len(args) == 1 and inspect.isfunction(args[0]):
            #we assume that the decorator has been declared with no arguments,
            #so go to straight to __call__, don't need __init__
            #if it's the case that the wrapped 'main' method allows or
            #expects a function as its first (and only) positional argument
            #then you can't use this decorator
            return obj(args[0])
        else:
            return obj


    def __init__(self, *args, **kw):
        self.args = args
        self._parser = kw.pop('parser', None)
        self.kwargs.update(kw)

    def _updatekwargs(self, dict):
        #don't want default null values of parser to overwrite anything
        #passed to `mainmethod` itself
        for k,v in dict.iteritems():
            #can't do 'if v: ...' because empty configobj evaluates False
            if v is None or v == '':
                continue
            self.kwargs[k] = v

    def exit(self):
        try:
            log.end()
        except:
            pass

    def run(self):
        options, args = self.parser.parse_args()
        #the following so that command line options are made available
        #to the decorated function as **kwargs
        self._updatekwargs(self.parser.values.__dict__)
        logargs = (
                self.kwargs.get(OPTLOGFILE, None),
                self.kwargs.get(OPTLOGDIR, None),
                self.kwargs.get(OPTLOGPREFIX, ''),
                )
        self.kwargs[OPTLOGFILE] = logstart(*logargs)
        log.info("SCRIPT: " + sys.argv[0])
        conf = self.kwargs.get(OPTCONFIG, None)
        if conf:
            log.info("%s: %s" % (OPTCONFIG.upper(), conf.filename))
        for k,v in self.kwargs.iteritems():
            if v and k not in COMMONOPTNAMES:
                log.info("%s = %s" % (k, v))
        log.divider()
        try:
            self.func(*self.args, **self.kwargs)
        except Exception, e:
            log.exception(str(e))
            log.info("Logfile: " + self.kwargs[OPTLOGFILE])
            sys.exit(1)
        log.info("Logfile: " + self.kwargs[OPTLOGFILE])
        sys.exit(0)

    def __call__(self, f):
        if f.func_globals['__name__'] == '__main__':
            self.func = f
            import atexit
            atexit.register(self.exit)
            atexit.register(self.run)
        return f

# Implementation of Ticker class
class Ticker(threading.Thread):
    def __init__(self, msg):
	threading.Thread.__init__(self)
	self.msg = msg
	self.event = threading.Event()
    def __enter__(self):
	self.start()
    def __exit__(self, ex_type, ex_value, ex_traceback):
	self.event.set()
	self.join()
    def run(self):
	sys.stdout.write(self.msg)
	while not self.event.isSet():
	    sys.stdout.write(".")
	    sys.stdout.flush()
	    self.event.wait(1)

