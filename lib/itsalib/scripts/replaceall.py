
'''
===============================================================================
SCRIPT: replaceall.py
===============================================================================

Replaces all instances of a specified string with another string in
every file in a given directory (and every subdirectory).  You can
optionally specify that only certain files are changed, and that certain
subdirectories are ignored.

Usage
-------------------------------------------------------------------------------

python replaceall.py <directory> <pattern> <replacement> [--globs=] [--ignoredirs=]

* <directory> - the root directory to make replacements
* <pattern>   - a regular expression pattern to be replaced
* <replacement> - the string with which you want to replace every occurrence of <pattern>
* [--globs=] - an optional semi-colon delimited list of filepatterns, only files which match one of these patterns will be changed
* [--ignoredirs=] - an optional semi-colon delimited list of directories to be ignored

EXAMPLE: python replaceall.py /foo/bar MP4 MP5

EXAMPLE: python replaceall.py /foo/bar yes no --globs=*.txt;*.doc

EXAMPLE: python replaceall.py /foo/bar yes no --globs=*.txt;*.doc --ignoredirs=.svn;bin

'''

CONFIRM = '''

This script is about to change this value:

    %s

to this value:

    %s

in every file in this directory:

    %s

(and all subdirectories), which satisfy this pattern:

    %s
%s
If you are sure, type y then <Return>.

If you are not sure, press <Return>.

'''

from itsalib import *

__all__ = ['CONFIRM']

def main(root, patt, repl, globs='*', ignoredirs=None):
    rewrite_all(dir, {patt: repl}, globs=globs, ignoredirs=ignoredirs)

if __name__ == '__main__':

    if not len(ARGS) > 2:
        sys.exit(USAGE)
    init(**KWARGS)
    dir = ARGS[0]
    pattern = ARGS[1]
    replacement = ARGS[2]
    globs = KWARGS.get('globs', '*')
    ignoredirs = KWARGS.get('ignoredirs', None)

    assert_path(dir)

    if ignoredirs:
        ignoring = "\n(Ignoring directories: %s)\n" % ignoredirs
    else:
        ignoring = ""

    ret = raw_input(CONFIRM % (pattern, replacement, dir, globs, ignoring))
    if ret and ret.lower() == 'y':
        main(dir, pattern, replacement, globs=globs, ignoredirs=ignoredirs)
    else:
        print
        print "ACTION CANCELLED"
        print




