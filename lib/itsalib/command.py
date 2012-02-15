'''
=================
`command` module
=================

Execute shell and system-level commands.

'''

__docformat__ = "restructuredtext en"
__author__ = "Gerard Flanagan <gerard.flanagan@euroclear.com>"

import subprocess
from subprocess import Popen, PIPE, STDOUT
import os


__all__ = ['popen', 'pipe', 'spawn', 'shell', 'ExternalCommandException']

class ExternalCommandException(OSError):
    pass


def call(cmdline):
    retcode = subprocess.call(cmdline, shell=False)
    if retcode < 0:
        raise Exception("Subprocess was terminated by signal %s" % -retcode)

def popen(cmdline):
    '''
    Execute an external command.
    '''
    fd = os.popen(cmdline)
    for line in fd:
        yield line.strip()
    fd.close()

def pipe(cmd1, cmd2):
    '''
    Pipe the result of one command to another.
    '''
    p1 = Popen(cmd1, stdout=PIPE)
    p2 = Popen(cmd2, stdin=p1.stdout, stdout=PIPE)
    return p2.communicate()[0]

def spawn(cmdline, env=None):
    '''
    Execute an external program and immediatley return control.
    '''
    return Popen(cmdline).pid

def shell(cmdline, env=None):
    '''
    Execute an external command via the shell.

    :param cmdline: Command and arguments as a single string
    :param env: A dictionary of environment variables to associate with the process.
    '''
    p = Popen(cmdline, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, env=env)
    p.wait()
    ret = p.stdout.readlines()
    if p.returncode != 0:
        raise ExternalCommandException(''.join(ret))
    return ret 

