
from itsalib.templates import BracesTemplate

class StartJythonUnix(BracesTemplate):
    r"""
    #!/usr/bin/ksh
    
    java \
            -Dpython.home={{jythonhome}} \
            -classpath {{jythonhome}}/jython.jar:$CLASSPATH \
            org.{{VAR}}python.util.jython.class

    """

import sys

#StartJythonUnix.write(sys.stdout, jythonhome="QQQ")

print StartJythonUnix.getvarset()
