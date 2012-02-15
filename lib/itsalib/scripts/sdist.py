
'''
===============================================================================
SCRIPT: sdist.py
===============================================================================

Create a python distribution package, then commit 
the resulting distribution to a subversion repository.

This script executes the supplied python build script (by convention, this should
be called `build.py`).  The exact functionality of `build.py` will depend
upon the particular project being packaged, but it is expected that it will
create either a compressed distributable archive or some form of binary install package.

For a standard pure python project it may be simply:

.. sourcecode:: python

    import os
    os.system('python setup.py sdist')

This will create a standard python package which can then be installed (after unzipping or
untarring) with `python setup.py install`.

As this is intended for official releases, this script should only be applied to a 'tagged' release.
(In Subversion terminology, a 'tag' is a source code branch that is considered to be frozen, ie.
it will not see any more development.)

WARNING: If there is an existing directory called `dist` in the same directory as the build
script, then it will be deleted.

Usage
-------------------------------------------------------------------------------

python sdist.py <buildscript> [svnhost]

* <buildscript> - python build script (required) 
* [svnhost]  - the host name or url of the subversion server (optional, defaults to localhost)

Example:

.. sourcecode:: python

    python sdist.py  "c:/myproj/build.py" 10.245.20.253


'''
SVNSERVER = "localhost"

from itsalib import *

def _svn_list(url):
    svncmd = 'svn list %s' % url
    return [line.strip() for line in shell(svncmd)]

def main(buildscript, svnserver):

    svndisturl = 'svn://%s/euroclear/dist' % svnserver

    distdir = os.path.join(os.path.dirname(buildscript), 'dist')

    if os.path.exists(distdir):
        log.info("Removing existing dist directory")
        removetree(distdir)

    mkdir(distdir)

    ###############################################
    log.info("Listing euroclear dist directory.")
    before = _svn_list(svndisturl)

    for item in before:
        log.info(item)

    #Now we rely on the buildscript to populate the 'dist' directory
    logfile = KWARGS.get('LOGFILE', None)
    setupcmd = 'python %s' % buildscript
    if logfile:
        setupcmd += ' --LOGFILE=%s' % logfile
    os.system(setupcmd)

    newfiles = [f for f in listdir(distdir) if isfile(join(distdir, f))]

    if not newfiles:
        log.info("Build script did not create any new files. No action taken.")
    else:
        log.info("New files created:")
        for f in newfiles:
            log.info(os.path.join(distdir, f))
        svnmsg = "Importing new files into '%s'" % svndisturl
        svncmd = 'svn import -m "%s" %s %s' % (svnmsg, distdir, svndisturl) 
        shell(svncmd)
    log.info("Removing dist directory: %s", distdir)
    #removetree(distdir)




if __name__ == '__main__':
    if not ARGS:
        sys.exit(__doc__)
    else:
        init(**KWARGS)
        buildscript = ARGS[0]
        if not exists(buildscript):
            sys.exit("ERROR: couldn't find file: `%s`" % buildscript)
        if len(ARGS) == 2:
            svnserver = ARGS[1]
        else:
            svnserver = SVNSERVER 
        main(buildscript, svnserver)


