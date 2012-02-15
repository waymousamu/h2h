'''
===============================================================================
SCRIPT: denonce.py
===============================================================================

Replace the `nonce` attribute in Authentication Service application
deployment descriptors.

Requirements
------------

- The **jar** utility from the Java sdk must be on the user's path.
- Python 2.5
- itsalib 1.8

Usage
-----

The script takes a single parameter: the path to the Authentication
Service EAR file.

.. sourcecode:: python

    python denonce.py <path-to-ear-file>

Example
-------

.. sourcecode:: python

    python denonce.py c:/temp/AuthServiceExtEAR.ear

Remarks
-------

The script works like this:

- Unzips the EAR file
- Unzips the Auth Service web module
- In the web module's WEB-INF directory does a search and replace in the file
  `ibm-webservices-ext.xmi`, replacing anything which matches the regular
  expression **<nonce .\*?/>** with an empty string.
- Rezips the contents of EAR and web module
- Displays diff (if any) of `ibm-webservices-ext.xmi`, before and after replacement

Originally tried using Python's `zipfile` module but it didn't seem to handle
certain jar files. But there are updates to `zipfile` in Python 2.6, so
maybe try again in future.

'''

from itsalib import *
from difflib import context_diff

AUTHSERVICEGLOB = '*AuthServiceExt.war'
XMIFILE = 'ibm-webservices-ext.xmi'
FILEPATTERNS = [AUTHSERVICEGLOB + join('*WEB-INF', XMIFILE)]

NONCEPATTERN = '<nonce .*?/>'
#NONCEPATH = 'wsDescExt/pcBinding/serverServiceConfig/securityRequestConsumerServiceConfig/requiredConfidentiality/nonce'

_DEBUG = False

@log.step
def display_diff(before, after):
    log.info("Creating diff of xmi file before and after replacements.")
    x = open(before).readlines()
    y = open(after).readlines()
    diff = context_diff(x, y)
    changed = False
    for line in diff:
        s = line.strip()
        if s:
            changed = True
            log.info(s)
    if not changed:
        log.warning("There were no differences in the two files, therefore no replacements were made.")

def main(infile, **kw):
    assert_isfile(infile)
    bak = backup(infile)
    parent = dirname(infile)
    root = None
    try:
        root = unjartree(infile, patterns=[AUTHSERVICEGLOB])
        files = list(findfiles(root, patterns=FILEPATTERNS))
        if not files:
            raise Exception("Didn't find deployment descriptor: " + XMIFILE)
        xmi = files[0]
        log.info("Found deployment descriptor: " + xmi)
        xmi_parts = os.path.splitext(XMIFILE)
        xmi_before = join(parent, "%s-before%s" % xmi_parts)
        xmi_after = join(parent, "%s-after%s" % xmi_parts)
        log.info("Backing up deployment descriptor.")
        copyfile(xmi, xmi_before)
        #xml_update(files[0], removes=[NONCEPATH])
        search_and_replace(xmi, NONCEPATTERN, '')
        copyfile(xmi, xmi_after)
    except Exception, e:
        log.error("There was an error. Tidying up then re-raising exception.")
        if exists(infile):
            remove(infile)
        rename(bak, infile)
        if root and not _DEBUG:
            removetree(root)
        raise
    jartree(root)
    display_diff(xmi_before, xmi_after)


if __name__ == '__main__':
    if len(ARGS) < 1:
        sys.exit("Missing command line argument. You must supply filepath to EAR file.")
    init(**KWARGS)
    try:
        main(ARGS[0], **KWARGS)
    except Exception, e:
        log.error(str(e).replace('%', '%%'))

