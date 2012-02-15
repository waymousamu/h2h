'''
======================
`utils` module
======================

Utility functions and classes.

'''

__docformat__ = "restructuredtext en"
__author__ = """
Gerard Flanagan <gerard.flanagan@euroclear.com>
Jeremie Chevalier <jeremie.chevalier@euroclear.com>
"""

import ConfigParser as conf
import inspect
import sys, os
from datetime import datetime
from itsalib import logger

__all__ = [
        'get_main_dir', 'get_timestamp', 'get_datestamp', 'get_datetimestamp',
        'mainmethod', 'ConfigParser', 'configobj_flatten',
        ]

__doc_all__ = __all__

def configobj_flatten(c):
    """
    Create a dictionary of all keys in a configobj instance.
    """
    d = {}
    def addkeyval(section, key):
        d[key] = section[key]
    c.walk(addkeyval)
    return d

def get_main_dir():
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0]) 

def _get_timestamp(dt) :
	'''
	Provides a timestamp from the passed `datetime` object, 
	where the timestamp is of the form HHMMSS (H for hour,
	M for minute and S for second).

	:param dt: `datetime` object to print timestamp from
	:return timestamp string of the form HHMMSS
	'''

	timestamp = [dt.hour, dt.minute, dt.second]
	result = ''
	for element in timestamp :
		if int(element) < 10 :
			result += "0"
		result += str(element)
	
	return result


def _get_datestamp(dt) :
	'''
	Provides a datestamp from the passed `datetime` object, 
	where the datestamp is of the form YYYYMMDD (Y for year,
	M for month and D for day).

	:param dt: `datetime` object to print datestamp from
	:return datestamp string of the form YYYYMMDD
	'''

	datestamp = [dt.year, dt.month, dt.day]
	result = ''
	for element in datestamp :
		if int(element) < 10 :
			result += "0"
		result += str(element)
	
	return result

def _get_datetimestamp(dt) :
	'''
	Provides a datetimestamp from the passed `datetime` object, 
	where the datetimestamp is of the form YYYYMMDD_HHMMSS (Y for year,
	M for month, D for day, H for hour, M for minute and S for second).

	:param dt: `datetime` object to print datetimestamp from
	:return datetimestamp string of the form YYYYMMDD_HHMMSS
	'''

	result = _get_datestamp(dt) + '_' + _get_timestamp(dt) 
	
	return result

def get_timestamp() :
	'''
	Provides a timestamp for the current time, where the timestamp 
	is of the form HHMMSS (H for hour, M for minute and S for second).

	:return current time timestamp string of the form HHMMSS
	'''

	return _get_timestamp(datetime.now())

def get_datestamp() :
	'''
	Provides a datestamp for the current date, where the datestamp 
	is of the form YYYYMMDD (Y for year, M for month and D for day).

	:return current date datestamp string of the form YYYYMMDD
	'''

	return _get_datestamp(datetime.now())

def get_datetimestamp() :
	'''
	Provides a datetimestamp for the current date and time, where 
	the datetimestamp is of the form YYYYMMDD_HHMMSS (Y for year, M 
	for month, D for day, H for hour, M for minute and S for second).

	:return current date and time datetimestamp string of the form 
	YYYYMMDD_HHMMSS
	'''

	return _get_datetimestamp(datetime.now())

def run_as_script(func):
    args = sys.argv[1:]
    func(*args)

def mainmethod(main):
    '''
    A function decorator designed to reduce boilerplate code in
    the `wasdeploy` scripts.  Each script has a similar 'modus
    operandi' - a main function which reads a config file and
    starts logging - so we try to do it here in order to avoid
    repeating code.

    :param main: A function taking at least `config` and `logfile` arguments, plus any number of additional positional arguments.
    '''
    import functools
    @functools.wraps(main) #New in Python2.5
    def inner(config, logfile, *args):
        if isinstance(config, str):
            conf_file = config
            config = ConfigParser()
            config.readfp(open(conf_file))
        logger.start(logfile=logfile)
        sourcefile = inspect.getabsfile(main)
        logger.info('*** Starting logger ***')
        logger.info('*** Running file %s ***' % sourcefile)
        try:
            main(config, logfile, *args)
        except:
            logger.exception("Unexpected Error.")
        logger.info('*** Leaving file %s ***' % sourcefile)
        logger.info('*** Stopping logger ***')
        logger.end()
    return inner

class ConfigParser(conf.ConfigParser):
    '''
    A subclass of the ConfigParser class from the ConfigParser module in the standard
    library which preserves the case of keys.
    ConfigParser keys are lower-cased by default, which causes problems when
    sending options to the WebSphere utility scripts, so this
    subclass allows mixed-case keys. Also causing an issue is the fact that the
    `items()` method includes any items in the [DEFAULT] section, so this is
    overridden here. Finally, I've added a prefix option to the `sections()`
    method so that you can group config sections with prefixes.
    '''
    def optionxform(self, key):
        return key

    def sections(self, prefix=''):
        return [ s for s in conf.ConfigParser.sections(self) if s.startswith(prefix) ]

    def items(self, section, vars=None):
        return [ (key, val) for (key, val) in conf.ConfigParser.items(self, section, vars=vars) if key not in self._defaults ]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

