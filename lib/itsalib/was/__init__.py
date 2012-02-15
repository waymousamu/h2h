"""
WebSphere-related utilities.
"""

import sys
import gsk

SHELL_EXTENSION = '.sh'

if sys.platform.lower().startswith('win'):

    SHELL_EXTENSION = '.bat'

