"""
===============================================================================
`itsalib.core.ftp`
===============================================================================

File transfer Protocol (FTP) module.
"""

import ftputil, os
from itsalib import logger as log

__all__ = [
        'connect', 'close', 'mkdir', 'chdir', 'cwd',
        'rename', 'upload', 'download',
        ]

host = None
hostname = None

def connect(server, user, pwd):
    global host, hostname
    host = ftputil.FTPHost(server, user, pwd)
    hostname = server

def close():
    _log_info('Disconnecting.')
    host.close()

def _log_info(msg):
    log.info('%s - %s' % (hostname, msg))

def _mkdir(dir):
    _log_info('Create directory: %s' % dir)
    host.mkdir(dir)

def mkdir(dir):
    directories = dir.split(host.sep)
    dir = ''
    while directories:
        dir = host.path.join(dir, directories.pop(0))
        if not host.path.isdir(dir):
            _mkdir(dir)

def chdir(dir):
    _log_info('Change directory: %s' % dir)
    host.chdir(dir)

def cwd():
    return host.getcwd()

def rename(src, dest):
    _log_info('Rename: %s to %s' % (src, dest))
    host.rename(src, dest)

_modes = ('', 'b')

def _upload(src, dest, binary=False):
    _log_info('Uploading file: %s to %s' % (src, dest))
    host.upload(src, dest, _modes[binary])

def _upload_dir(src, dest, binary=False):
    pass

def upload(src, dest, binary=False):
    if os.path.isfile(src):
        _upload(src, dest, binary)
    else:
        _upload_dir(src, dest, binary)


def download(src, dest, binary=False):
    _log_info('Downloading file: %s to %s' % (src, dest))
    host.download(src, dest, _modes[binary])


