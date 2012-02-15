
from itsalib import *
from itsalib.scriptmate import mainmethod, CommonOptionParser

ERRMSGBADARGS = "Bad command line.\n"

USAGE = """
python %prog <directory> [options]
python %prog --help
"""


optparser = CommonOptionParser(noconfig=True, usage=USAGE)

@mainmethod(parser=optparser, logprefix='itsa-make-tree-readable-')
def main(*args, **kw):
    if len(args) != 1:
        log.error(ERRMSGBADARGS)
        optparser.print_help()
        print
        sys.exit(1)
    else:
        rootdir = args[0]
        assert_path(rootdir)
        for f in findfiles(rootdir):
            make_readable(f)
            



