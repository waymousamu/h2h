"""
====================================================
 `itsalib.deploytools`
====================================================

A collection of functions for common software deployment tasks.
"""

__docformat__ = "restructuredtext en"
__author__ = "Gerard Flanagan <gerard.flanagan@euroclear.com>"

__all__ = [
        'os', 'sys',
        'call', 'popen', 'shell', 'spawn',
        'ARGS', 'KWARGS', 'SHELL_EXT',
        'CONFIGKEY', 'CONFIGSPECKEY',
        'LOGFILEKEY', 'LOGDIRKEY', 'LOGFILEPREFIXKEY',
        'log', 'logstart', 'setecholevel', 'setloglevel',
        'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
        'iglob', 'StringIO',
        'init',
        'curdir', 'pardir', 'isdir', 'isfile', 'islink', 'sep', 'pathsep',
        'devnull', 'join', 'split', 'exists',
        'normpath', 'abspath', 'basename', 'dirname',
        'cwd', 'chdir', 'mkdir',
        'listdir', 'listdirs', 'walkdir', 'find', 'findfiles',
        'mktempdir', 'mktempfile', 'StringTemplate',
        'openfile', 'copy', 'copyfile', 'copytree', 'updatetree',
        'mirrortree', 'remove', 'removetree',
        'rename', 'chmod', 'chown', 'cat',
        'multireplace', 'multireplacen', 'write_string', 'rewrite_template',
        'rewrite_file', 'rewrite_all', 'search_and_replace',
        'xml_update', 'xml_find',
        'tardir', 'untar', 'zipdir', 'unzip',
        'jardir', 'unjar', 'jartree', 'unjartree',
        'email',
        'timestamp',
        'DeploytoolsException',
        'assert_path', 'assert_isfile',
        'backup', 'get_svn_revision', 'make_readable',
        ]

__doc_all__ = __all__[:]

for item in ['os', 'sys', 'log']:
    __doc_all__.remove(item)

import os, sys, shutil, tempfile, stat, re
from os.path import (join, split, exists, dirname, basename, normpath, abspath, curdir, pardir, isdir, isfile, islink, sep, pathsep, devnull)
#from itsalib import logger as log
import logger as log
import command
from logging import (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
from itsalib.util import get_datetimestamp as timestamp
from itsalib.util import configobj
from itsalib.util import elementfilter
from itsalib.template import *
from string import Template as StringTemplate
from glob import iglob
import fnmatch
import tarfile, zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cStringIO import StringIO
import imp
import __main__ as CALLER

setecholevel = log.setecholevel 
setloglevel = log.setloglevel 
SHELL_EXT= '.sh'

if sys.platform.lower().startswith('win'):
    SHELL_EXT= '.bat'

try:
    from functools import update_wrapper
except ImportError:
    def update_wrapper(*args):
        pass

SMTP_SERVER = 'pwnotgtw1.beprod01.eoc.net' #'10.224.130.47' 

class DeploytoolsException(Exception):
    pass


def assert_path(fpath):
    '''
    Raise a Deploytools exception if `fpath` is a nonexistent filepath.
    '''
    if not exists(fpath):
        raise DeploytoolsException('Nonexistent path: ' + fpath)

def assert_isfile(fpath):
    '''
    Raise a Deploytools exception if `fpath` is not a file.
    '''
    if (not os.path.isfile(fpath)) or (os.path.islink(fpath)):
        raise DeploytoolsException("Not a file: %s" % fpath)

def backup(src):
    '''
    Make a timestamped copy of the file `src`
    '''
    log.info("Making a backup of file: " + src)
    assert_isfile(src)
    name, ext = os.path.splitext(src)
    src_copy = "%s-%s%s" % (name, timestamp(), ext)
    copyfile(src, src_copy)
    return src_copy
    
def _getargs():
    script = sys.argv[0]
    allargs = sys.argv[1:]
    args = []
    kwargs = {}
    key = None
    while allargs:
        arg = allargs.pop(0)
        if arg.startswith('--'):
            parts = arg.split('=', 1)
            key = parts[0][2:]
            if len(parts) > 1:
                arg = parts[1]
            else:
                if not allargs or allargs[0].startswith('-'):
                    allargs.insert(0, 'yes')
                continue
        elif arg.startswith('-'):
            key = arg[1:]
            if not allargs or allargs[0].startswith('-'):
                allargs.insert(0, 'yes')
            continue
        if key is None:
            args.append(arg)
        else:
            kwargs[key] = arg
            key = None
    return script, args, kwargs

SCRIPT, ARGS, KWARGS = _getargs()

def _assert_req_args(req_args, got_args):
    error = False
    for x in set(arg[0] for arg in req_args) - set(got_args.keys()):
        raise Exception("Missing command line argument: '%s'." % x)
        error = True
    for arg, vals, _ in req_args:
        if vals and (got_args[arg] not in vals):
            raise Exception("Invalid command line argument: '%s'." % arg)
            error = True
    if error:
        if hasattr(CALLER, 'USAGE'):
            sys.exit(CALLER.USAGE)
        else:
            msg = 'Required arguments:\n'
            for key, vals, help in req_args:
                msg += str(key)
                if vals:
                    msg += '    %s' % vals
                if help:
                    msg += '    %s' % help
                msg += '\n'
            sys.exit(msg)

@log.step
def call(cmdline):
    log.info("Running external command: " + cmdline)
    command.call(cmdline)

@log.step
def popen(cmdline):
    '''
    Run an external system-level command.

    * cmdline: The command string to be run.
    
    >>> popen('jar xvf "My Jarfile.jar"')
    '''
    log.info("Running external command: " + cmdline)
    ret = []
    for line in command.popen(cmdline):
        ret.append(line)
        log.info("OUTPUT: " + line.replace('%', '%%'))
    log.info("Done.")
    return ret

@log.step
def shell(cmdline):
    '''
    Run an external command through the shell.

    * cmdline: The command string to be run.
    '''
    log.info('Running shell command: %s' % cmdline)
    return command.shell(cmdline)

@log.step
def spawn(cmdline):
    '''
    Spawn an external process.

    >>> spawn('notepad "output.log"')
    '''
    log.info("Spawning external process: " + cmdline)
    return command.spawn(cmdline)

def logstart(logfile=None, logdir=None):
    '''
    Initialise file and console loggers.

    * logdir: The directory where the timestamped log file will be saved.
    * logfile: If `logdir` is not specified, log to this file.

    :return: The log file path.
    '''
    logfile = log.start(logfile, logdir)
    log.divider()
    if logfile:
        log.info("Started logger. Logging to file: '%s'" % logfile)
    else:
        log.info("Started logger. A log file or log directory was not specified.")
    return logfile

CONFIGKEY = 'config'
LOGFILEKEY = 'logfile'
LOGFILEPREFIXKEY = 'logfileprefix'
LOGDIRKEY = 'logdir'
CONFIGSPECKEY = 'configspec'

def init():
    '''
    Set up logging and load configuration data.
    
    This is intended for use by scripts and is intended to remove boilerplate code.
    Typically a script will require a log file (or directory) and a config
    (or properties) file to be passed as command line options.  `init` will look
    for any of the following in `KWARGS` (keyword arguments):

    * logdir
    * logfile
    * config
    * configspec


    '''
    global KWARGS
    if CONFIGSPECKEY in KWARGS:
        configspec = configobj.ConfigObj(StringIO(KWARGS[CONFIGSPECKEY]), list_values=False)
    else:
        configspec = None
    configfile = KWARGS.get(CONFIGKEY, None)
    if configfile is not None:
        #isinstance check to see if a file name has been passed
        #necessary because the caller is free to pass something else
        #suitable for creating a ConfigObj, eg. a list of strings
        if isinstance(configfile, basestring) and not exists(configfile):
            raise OSError('Config file doesn\'t exist: %s' % configfile)
        else:
            config = configobj.ConfigObj(configfile, configspec=configspec, write_empty_values=True)
            if configspec is not None:
                from itsalib.util.validate import Validator
                vdt = Validator()
                result = config.validate(vdt)
                if result is not True:
                    msg = 'Validation Errors.\n\n'
                    for item in configobj.flatten_errors(config, result):
                        msg += ' %s:%s:%s\n' % item
                    msg += '\n%s\n' % configspec
                    sys.exit(msg)
            #replace the configkey value with an actual instance of a configobj
            KWARGS[CONFIGKEY] = config
    logfile = logstart(KWARGS.get(LOGDIRKEY, None), 
                        KWARGS.get(LOGFILEKEY, None),
                        KWARGS.get(LOGFILEPREFIXKEY, ''))
    KWARGS[LOGFILEKEY] = logfile
    if hasattr(CALLER, '__file__'):
        calling_script = abspath(CALLER.__file__)
        log.info("SCRIPT: '%s'" % calling_script)
    if configfile and config.filename:
        log.info("CONFIGURATION file: '%s'" % abspath(config.filename))
    for i,arg in enumerate(ARGS):
        log.info("arg%s = %s" % (i,arg))
    for key, val in KWARGS.iteritems():
        if not key.startswith('config'):
            log.info("%s = %s" % (key, val))
    log.divider()
    return logfile
    
#if hasattr(CALLER, '__name__') and CALLER.__name__ == '__main__':
#    init(**KWARGS)


def make_readable(fpath):
    '''
    On windows, this will make a read-only file readable.
    '''
    mode = os.stat(fpath)[stat.ST_MODE] | stat.S_IREAD | stat.S_IWRITE
    chmod(fpath, mode)

#
def openfile(fpath, mode='r'):
    '''
    Open a file.  By default the file will be opened for reading.

    * fpath: The file to open.
    * mode: The file mode - one of ['r', 'w', 'a', 'rb', 'wb', 'ab']

    :return: A file object.
    '''
    msg = "Opening file for %s: '%s'"
    if mode[0] in ['w', 'a']:
        dir = dirname(fpath)
        if dir and not exists(dir):
            mkdir(dir)
        msg %= ('writing', fpath)
    else:
        msg %= ('reading', fpath)
    log.info(msg)
    try:
        return open(fpath, mode)
    except:
        log.info("Unable to open file. Trying to make change permissions: '%s'" % fpath)
        make_readable(fpath)
        log.info(msg)
        return open(fpath, mode)


def chmod(fpath, mode):
    '''
    Change a file's permissions.

    * mode: See documentation for the stdlib's `stat` module.
    '''
    if mode is None:
        return
    perms = os.stat(fpath)[stat.ST_MODE]
    log.info('Changing permissions of file \"%s\" from %s to %s' % (fpath, perms, mode))
    os.chmod(fpath, mode)


def chown(fpath, uid, gid):
    '''
    Change a file's ownership.

    * uid: User id.
    * gid: Group id.
    '''
    log.info('Changing ownership of file %s to %s:%s' % (fpath, gid, uid))
    os.chown(fpath, uid, gid)


def rename(src, dest):
    '''
    Rename a file or directory.

    * src: Original file or directory name.
    * dest: The new name.
    '''
    if isdir(src):
        ftype = "directory"
    else:
        ftype = "file"
    log.info('Renaming %s: %s -> %s' % (ftype, abspath(src), abspath(dest)))
    os.rename(src, dest)

def cwd():
    '''
    Get the current working directory.

    :return: String
    '''
    return os.getcwd()


def chdir(dir):
    '''
    Change working directory to `dir`.

    * dir: The new directory filepath.
    '''
    log.info('Changing directory to %s' % abspath(dir))
    os.chdir(dir)

#The following is the `makedirs()` function from the os module with logging added

def mkdir(name, mode=0777):
    """
    Create a directory. If any subdirectory of `name` does not exist, then it too will be created.
    """
    name = normpath(name)
    head, tail = split(name)
    if not tail:
        head, tail = split(head)
    if head and tail and not exists(head):
        mkdir(head, mode)
        if tail == curdir:           # xxx/newdir/. exists if xxx/newdir exists
            return
    log.info('Creating directory: %s' % name)
    os.mkdir(name, mode)
    return abspath(name)


def listdir(dir=None):
    '''
    List contents of directory `dir`. If `dir` is not specified then the
    contents of the current working directory are listed.

    * dir: Directory filepath.

    :return: A list.
    '''
    return os.listdir(dir or curdir)


def listdirs(dir=None):
    '''
    List contents of `dir` as well as the contents of any subdirectory, and this recursively.
    Returned filepaths are relative to `dir`.

    * dir: Directory filepath.

    :return: A list.
    '''
    return list(walkdir(dir, relative=True))

DEFAULTIGNOREDIRS = ['*.svn']

def walkdir(root=None, relative=False, ignoredirs=None):
    '''
    Recursively walk a directory tree.
    Note: by default, Subversion data directories are ignored, ie. any directory whose last component is '.svn' -
    to change this, set ignoredirs=[].

    * root: The root of the directory tree. If not specified, defaults to the current working directory.
    * relative: If set to True, then returned filepaths will be relative to `root`, otherwise they will be absolute.
    * ignoredirs: A list of `glob` patterns.  If any subdirectory matches any of these patterns, it (and its contents) will be ignored.

    :return: This is an iterator.
    '''
    if ignoredirs is None:
        ignoredirs = DEFAULTIGNOREDIRS
    if root:
        root = normpath(root)
    else:
        root = os.getcwd()
    stack = [root]
    while stack:
        dir = stack.pop(0)
        for f in (join(dir, fname) for fname in os.listdir(dir)):
            if isdir(f) and not islink(f):
                #dname = basename(f)
                #if any(dname==pattern for pattern in ignoredirs):
                if any(fnmatch.fnmatch(f, pattern) for pattern in ignoredirs):
                    log.info('Ignoring directory: %s' % f)
                    continue
                else:
                    stack.append(f)
                    stack.sort()
            if relative:
                yield f.replace(root, '', 1)[1:]
            else:
                yield f

DEFAULTPATTERNS = ['*']


def find(root=None, patterns=None, ignoredirs=None):
    '''
    Search a directory tree for files and directories matching particular `glob` patterns.
    The default pattern list is ['*'], which will match any filepath.
    Note: by default, Subversion data directories are ignored, ie. any directory whose last component is '.svn' -
    to change this, set ignoredirs=[].

    * root: The root of the directory tree. If not specified, defaults to the current working directory.
    * patterns: A list of `glob` patterns.  Only filepaths matching one of these patterns will be returned.
    * ignoredirs: A list of `glob` patterns.  If any subdirectory matches any of these patterns, it (and its contents) will be ignored.

    :return: This is an iterator.
    '''
    patterns = patterns or DEFAULTPATTERNS
    for fname in walkdir(root, ignoredirs=ignoredirs):
        for pattern in patterns:
            if fnmatch.fnmatch(fname, pattern):
                yield fname
                break


def findfiles(root=None, patterns=None, ignoredirs=None):
    '''
    Find all files within a directory tree which match particular `glob` patterns.
    The default pattern list is ['*'], which will match any filepath.
    Note: by default, Subversion data directories are ignored, ie. any directory whose last component is '.svn' -
    to change this, set ignoredirs=[].

    * root: The root of the directory tree. If not specified, defaults to the current working directory.
    * patterns: A list of `glob` patterns.  Only filepaths matching one of these patterns will be returned.
    * ignoredirs: A list of `glob` patterns.  If any subdirectory matches any of these patterns, it (and its contents) will be ignored.

    :return: This is an iterator.
    '''
    for f in find(root, patterns, ignoredirs=ignoredirs):
        if isfile(f):
            yield f


def mktempdir():
    '''
    Create a temporary directory and return its absolute path.
    The directory is readable, writable, and searchable only by
    the creating user ID.

    :return: The absolute path of the temporary directory
    '''
    log.info('Creating temporary directory.')
    d = tempfile.mkdtemp()
    log.info('Temporary directory is: %s.' % d)
    return d

class TempFile(object):

    def __init__(self, fd, fname):
        self._fileobj = os.fdopen(fd, 'wb')
        self.name = fname

    def __getattr__(self, attr):
        return getattr(self._fileobj, attr)


def mktempfile(dir=None, prefix='itsa-', suffix='.tmp'):
    '''
    Create a temporary writable file object.

    * dir: A directory filepath in which the temporary file will be created.
    * suffix: The suffix (extension) of the created file. By default, this is '.tmp'.

    :return: The path of the file object.
    '''
    if dir:
        log.info("Creating temporary file in directory: '%s'" % dir)
    else:
        log.info('Creating temporary file.')
    f = TempFile(*tempfile.mkstemp(dir=dir, prefix=prefix, suffix=suffix))
    log.info('Temporary file is: %s.' % f.name)
    return f


def copyfile(src, dst):
    '''
    Copy file `src` to file `dst`.  If `dst` exists (and is a file) then it will be overwritten.
    If `dst` is located in a non-existent directory, then that directory will automatically be created.

    * src: File to copy.
    * dst: Destination file.
    '''
    src = abspath(src)
    dst = abspath(dst)
    dir = dirname(dst)
    log.info('Copying file: %s to %s' % (src, dst))
    if not exists(src):
        raise OSError('Source file does not exist: %s' % src)
    elif isdir(src):
        raise OSError("Source must be a file not a directory")
    elif isdir(dst):
        raise OSError("Destination must be a file not a directory")
    if exists(dst):
        log.info('Destination file exists: replacing')
        remove(dst)
        log.info('Copying file: %s to %s' % (src, dst))
    if dir and not isdir(dir):
        mkdir(dir)
    shutil.copyfile(src, dst)
    shutil.copystat(src, dst)
    log.info("Done copying file.")

def copy(src, dst):
    '''
    Copy file `src` to directory `dst`.
    '''
    dst = join(dst, basename(src))
    copyfile(src, dst)
    return dst


@log.step
def copytree(src, dst, patterns=None, ignoredirs=None, update=False):
    '''
    Copy an entire directory tree from `src` to `dst`. The destination directory
    should not already exist, unless `update` is explicitly set to True, in
    which case files in `dst` will be replaced with their counterparts in `src`,
    if the counterpart matches any of the `patterns`.
    '''
    src = abspath(src)
    dst = abspath(dst)
    log.info('Recursive copy: %s to %s' % (src, dst))
    if not exists(src):
        raise OSError('Source directory does not exist: %s' % src)
    if exists(dst) and not update:
        raise OSError('Destination directory already exists: %s.' % dst)
    #dst = abspath(dst)
    for fpath in find(src, patterns, ignoredirs):
        fdstpath = fpath.replace(src, dst, 1)
        if isdir(fpath) and not isdir(fdstpath):
            mkdir(fdstpath)
        else:
            copyfile(fpath, fdstpath)

def updatetree(src, dst, patterns=None):
    return copytree(src, dst, patterns, True)

def mirrortree(src, dst, patterns=None):
    if exists(dst):
        removetree(dst, patterns)
    if exists(dst):
        updatetree(src, dst, patterns)
    else:
        copytree(src, dst, patterns)


def remove(fpath):
    '''
    Remove a file or directory.
    '''
    if isdir(fpath):
        func = os.rmdir
        ftype = 'directory'
    else:
        func = os.remove
        ftype = 'file'
    log.info('Removing %s: %s' % (ftype, fpath))
    try:
        func(fpath)
    except OSError, e:
        if e.errno == 13:
            #Permission denied
            make_readable(fpath)
            func(fpath)
        else:
            raise

@log.step
def removetree(dir, patterns=None):
    '''
    Recursively delete files and directories

    :return: None
    '''
    log.info('Recursive remove directory: %s ' % dir)
    patterns = patterns or DEFAULTPATTERNS
    for root, dirs, files in os.walk(dir, topdown=False):
        for f in files:
            for pattern in patterns:
                if fnmatch.fnmatch(f, pattern):
                    remove(join(root, f))
        for d in dirs:
            d = join(root, d)
            if not os.listdir(d):
                remove(d)
    if not os.listdir(dir):
        remove(dir)

def _write_string(sin, fout):
    closeit = False
    if not hasattr(fout, 'write'):
        fout = openfile(fout, 'wb')
        closeit = True
    log.info('Writing string to file: %s.' % fout.name)
    try:
        fout.write(sin)
    finally:
        if closeit:
            fout.close()

def _write_string_template(sin, fout, mapping):
    log.info('String template substitution.')
    for item in mapping.iteritems():
        log.info('Substituting %s -> %s' % item)
    t = StringTemplate(sin).safe_substitute(mapping)
    _write_string(t, fout)

def multireplacen(text, mapping, start='', end=''):
    log.info("Multiple pattern substitution.")
    keys = mapping.keys()
    keys.sort()
    keys.reverse()
    pattern = '|'.join(re.escape('%s%s%s' % (start, key, end)) for key in keys)
    rx = re.compile(pattern)
    i, j = len(start), len(end)
    def callback(match):
        key = match.group(0)
        #need len(key)-j rather than -j in case j is zero
        repl = mapping[key[i:len(key)-j]]
        log.info("Replacing '%s' with '%s'" % (key, repl))
        return repl
    return rx.subn(callback, text)

def multireplace(text, mapping, start='', end=''):
    '''
    Multiple pattern substitution in strings.

    * text: A string.
    * mapping: A dictionary of strings indexed by regular expressions.

    :return: The converted text.
    '''
    return multireplacen(text, mapping, start, end)[0]


def write_string(sin, fout, mapping=None):
    '''
    Write string `sin` to file `fout`.
    '''
    if mapping is None:
        _write_string(sin, fout)
    else:
        _write_string_template(sin, fout, mapping)


@log.step
def rewrite_template(tmpl, mapping, fout=None):
    '''
    Replace placeholders in a template file.

    * tmpl: A text file containing shell-style placeholders (eg. ${my_variable})
    * mapping: A dictionary of placeholder->replacement pairs.
    * fout: [optional] Write to this file rather than overwriting the template. 

    '''
    log.info('Rewriting template: %s' % tmpl)
    fout = fout or tmpl
    t = openfile(tmpl, 'rb')
    s = t.read()
    t.close()
    _write_string_template(s, fout, mapping)


@log.step
def rewrite_file(tmpl, mapping, fout=None):
    '''
    Replace text patterns in a text file.

    * tmpl: A text file.
    * mapping: A dictionary of pattern->replacement pairs.
    * fout: [optional] Write to this file rather than overwriting the original. 

    '''
    log.info('Rewriting file: %s' % tmpl)
    fout = fout or tmpl
    t = openfile(tmpl, 'rb')
    s = t.read()
    t.close()
    if '\0' in s:
        log.warning("%s seems to be a binary file. Ignoring it.", tmpl)
        return
    s, n = multireplacen(s, mapping)
    if n:
        write_string(s, fout)
        if n ==1:
            log.info("There was one change.")
        else:
            log.info("There were %s changes." % n)
    else:
        log.info("The specified pattern or patterns were not found in file '%s'. It was not rewritten." % tmpl)

def rewrite_all(dir, mapping, globs=None, ignoredirs=None):
    '''
    Replace string patterns in every file in a given directory, including subdirectories.
    '''
    for fpath in findfiles(dir, globs, ignoredirs):
        #fpath = join(dir, f)
        log.info("Backing up file: %s" % fpath)
        #copyfile(fpath, fpath + '.bak')
        rewrite_file(fpath, mapping)

@log.step
def search_and_replace(src, patt, repl, dst=None):
    log.info("Search and replace.")
    log.info("Regular expression: " + patt)
    log.info("Replacement: " + repl)
    dst = dst or src
    log.info("Outfile: " + dst)
    t = openfile(src, 'rb')
    s = t.read()
    t.close()
    s, n = re.subn(patt, repl, s)
    if n > 0:
        _write_string(s, dst)
        log.info("Number of changes: %s" % n)
    else:
        log.info("The pattern was not found. The file was not rewritten.")

@log.step
def cat(*args):
    '''
    Concatenate a list of files. 
    '''
    if len(args) < 2:
        return
    outfile = args[0]
    args = args[1:]
    if isfile(outfile):
        mode = 'a+b'
    else:
        mode = 'w+b'
    log.info("Concatenating files.")
    fout = openfile(outfile, mode)
    for fpath in args:
        f = open(fpath, 'r')
        try:
            for line in f:
                log.debug("Adding line: " + line.replace('%', '%%'))
                fout.write(line + '\n')
        finally:
            f.close()
    log.info("Done concatenating files.")


@log.step
def xml_update(infile, updates=[], removes=[], outfile=None, encoding='UTF-8'):
    '''
    Update or delete XML elements and attributes.

    * infile: The XML file to alter.
    * updates: A list of `filterpath, mapping` pairs where mapping is a dictionary of pattern->replacements.
    * removes: A list of filterpaths representing elements or attributes to delete from the source file.
    * outfile: Write the altered file to this file rather than overwriting the original.
    * encoding: The output file will be written with this encoding.
    '''
    from xml.etree import cElementTree as ET
    outfile = outfile or infile
    doc = ET.parse(infile)
    elem = doc.getroot()
    efilter = elementfilter.ElementFilter(elem)
    changes = 0
    log.info('Updating xml file: %s' % infile)
    for filterpath, pattern, repl in updates:
        log.info('Updating: %s' % filterpath)
        efilter.filter = filterpath
        changes += efilter.sub(pattern, repl)
    for filterpath in removes:
        log.info('Removing: %s' % filterpath)
        efilter.filter = filterpath
        changes += efilter.removeall()
    doc.write(outfile, encoding='UTF-8')
    log.info('Number of changes: %s' % changes)


@log.step
def xml_find(infile, filterpath):
    '''
    Find XML elements or attributes.
    '''
    log.info("Find XML elements or attributes. Filterpath is: " + filterpath)
    from xml.etree import cElementTree as ET
    log.info("Loading ElementTree instance from file: " + infile)
    doc = ET.parse(infile)
    elem = doc.getroot()
    return elementfilter.findall(elem, filterpath)

@log.step
def tardir(dir, dest=None, gzip=False):
    '''
    Compress a given directory into a TAR archive.
    '''
    dirpath = abspath(dir)
    dir = basename(dirpath)
    dest = abspath(dest or '%s.tar' % dir)
    mode = 'w'
    msg = ' '
    if gzip:
        mode += ':gz'
        dest += '.gz'
        msg += 'gzipped '
    log.info("Creating%star archive: '%s'" % (msg, dest))
    if exists(dest):
        log.info("Archive already exists: \'%s\' - removing" % dest)
        remove(dest)
    cwd = os.getcwd() #remember current directory
    log.debug("cwd: " + cwd)
    t = tarfile.open(dest, mode)
    try:
        chdir(dirname(dirpath)) #cd to parent of dir
        t.add(dir)
    finally:
        t.close()
        chdir(cwd) #cd back to original working directory
    log.info("Tar archive created. Archive contains the following files:")
    for f in sorted(walkdir(dirpath, relative=True)):
        log.info(join(dir,f))
    return dest

@log.step
def untar(src, dst=None):
    '''
    Uncompress a TAR archive.
    '''
    src = abspath(src)
    if not dst:
        dst = os.getcwd()
    dst = abspath(dst)
    log.info("Untarring archive: '%s' to directory '%s'" % (src, dst))
    if not exists(dst):
        mkdir(dst)
    before = listdir(dst)
    tar = tarfile.open(src)
    tar.extractall(dst)
    tar.close()
    log.info("Finished untarring. The following files were unpacked:")
    unpacked = sorted(join(dst, f) for f in listdir(dst) if f not in before)
    for f in unpacked:
        if isfile(f):
            log.info(f.replace(dst, '', 1)[1:])
        elif isdir(f):
            for t in walkdir(f):
                if isfile(t):
                    log.info(t.replace(dst, '', 1)[1:])

@log.step
def unzip(src, dest=None):
    '''
    Uncompress a ZIP archive.
    '''
    log.info('Unzipping file: %s' % src)
    assert_path(src)
    if not dest:
        dest = os.getcwd()
    elif not exists(dest):
        mkdir(dest)
    try:
        z = zipfile.ZipFile(src)
        fecked = False
    except:
        fecked = True
    if fecked:
        log.info("Couldn't open with zipfile. Trying with jar.")
        unjar(src)
    else:
        for name in z.namelist():
            fpath = join(dest, name)
            basedir = dirname(fpath)
            if not exists(basedir):
                mkdir(basedir)
            if not name.endswith('/'):
                destfile = open(fpath, 'w')
                destfile.write(z.read(name))
                destfile.close()
        z.close()
    
@log.step
def zipdir(src, dest=None):
    '''
    Compress a given directory into a ZIP archive.
    '''
    src = normpath(src)
    dest = dest or '%s.zip' % basename(src)
    log.info("Creating zip archive: '%s'" % dest)
    if exists(dest):
        log.info("Archive already exists: \'%s\' - removing" % dest)
        remove(dest)
    z = zipfile.ZipFile(dest, 'w')
    for f in findfiles(src):
        relative_name = normpath(f).replace(src, '', 1)[1:]
        z.write(f, relative_name)
    z.close()
    return dest

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#    JAVA UTILTIES
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

UNJARRABLE = ['*.ear', '*.jar', '*.war', '.zip']
UNJARSUFFIX = '.unjar$'
JARCMD = 'jar -cvfm "%s" META-INF/MANIFEST.MF .'
UNJARCMD = 'jar xvf'

@log.step
def unjar(src, dest):
    '''
    Unzip a zipped archive `src` to directory `dest` using the `jar` utility from the Java sdk.

    * Requires `jar` to be on the user's path.
    * This will work with .zip, .jar, .ear, and .war files.
    * If `dest` does not exist then it will be created.

    * src: A zip-compressed archive file.
    * dest: The directory to which the archive contents will be extracted.

    '''
    log.info("Unjar file: " + src)
    assert_path(src)
    assert_isfile(src)
    log.info("Destination directory is: " + dest)
    if not exists(dest):
        mkdir(dest)
    orig = cwd()
    chdir(dest)
    cmdline = ' '.join([UNJARCMD, '"%s"' % src])
    popen(cmdline)
    chdir(orig)
    log.info("Finished unjarring: " + src)

@log.step
def jardir(src, dest):
    '''
    Create a JAR archive `src` containing the contents of directory `dest`.

    * src: A directory.
    * dest: The name of the archive file to be created.

    '''
    log.info("Jarring directory: " + src)
    assert_path(src)
    log.info("Destination is: " + dest)
    chdir(src)
    cmdline = JARCMD % dest
    popen(cmdline)
    chdir(pardir)
    removetree(src)

def _unjartree(src, patterns=None):
    patterns = patterns or UNJARRABLE
    dest = src + UNJARSUFFIX
    unjar(src, dest)
    log.info("Remove original.")
    remove(src)
    for f in findfiles(dest, patterns=patterns):
        _unjartree(f)
    log.info("Finished recursive unjar.")
    return dest

@log.step
def unjartree(src, patterns=None):
    '''
    Unjar zipped archive file `src` and any other archives (eg. JAR, WAR) that
    `src` contains (and this recursively).

    * src: A zip-compressed archive file.

    :return: The name of the directory to which the archive is extracted.
    '''
    src = os.path.abspath(src)
    log.info("Recursive unjar: " + src)
    assert_path(src)
    #backup(src)
    return _unjartree(src, patterns)

def _rejardir(dir):
    dest = dir[:-len(UNJARSUFFIX)]
    jardir(dir, dest)
    return dest

@log.step
def jartree(src):
    '''
    Re-jar a directory `src` that has been unjarred with the `unjartree` function.

    An AssertionError will be raised if `src` does not end with the custom
    suffix created by `unjartree`.

    * src: An 'unjarred tree' directory.

    :return: The name of archive created. This will be `src` with the custom suffix removed.
    '''
    assert_path(src)
    assert src.endswith(UNJARSUFFIX)
    src = os.path.abspath(src)
    for root, dirs, _ in os.walk(src, topdown=False):
        for d in dirs:
            if d.endswith(UNJARSUFFIX):
                _rejardir(join(root, d))
    return _rejardir(src)

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


@log.step
def email(sender, recipients, subject, msg, attachments=None):
    '''
    Send an email via SMTP.

    * sender: The name to appear in the `From` field.
    * recipients: A list of recipient email addresses.
    * subject: The `Subject` field.
    * msg: The message to be sent (a string)
    * attachments: A list of files to be sent as attachments. Only text files are currently supported.

    '''
    #only text attachments supported
    log.info('Sending mail to: %s' % recipients)
    attachments = attachments or []
    if attachments:
        n = len(attachments)
        if n == 1:
            log.info('There is 1 attachment.')
        else:
            log.info('There are %s attachments.' % n)
        outer = MIMEMultipart()
        for fname in attachments:
            fp = open(fname)
            attachment = MIMEText(fp.read())
            fp.close()
            attachment.add_header('Content-Disposition', 'attachment', filename=fname)
            outer.attach(attachment)
        outer.attach(MIMEText(msg))
    else:
        log.info('There are no attachments.')
        outer = MIMEText(msg)
    outer['From'] = sender
    outer['To'] = ', '.join(recipients)
    outer['Subject'] = subject
    s = smtplib.SMTP(SMTP_SERVER)
    s.sendmail(sender, recipients, outer.as_string())
    s.close()
    

def get_svn_info():
    info = {}
    for line in popen('svn info'):
        name, sep, val = line.partition(':')
        if sep:
            info[name] = val.strip()
    return info

def get_svn_revision():
    return get_svn_info()['Revision']

