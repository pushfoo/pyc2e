"""
Imports classes that seem appropriate for current platform.

The dict SUPPORTED maps interface type names to their implementations. If it
isn't in the dict, it isn't believed to be supported on the current platform.
"""
import platform
from pyc2e.interfaces.interface import coerce_to_bytearray
from pyc2e.interfaces.unix import UnixInterface

WIN32 = 'win32'
UNIX = 'unix'

SUPPORTED = {
    UNIX: UnixInterface
}

LOCAL_PLATFORM = UNIX
DEFAULT_INTERFACE_TYPE = UNIX

# enable windows support on windows
if platform.system() == 'Windows':
    from pyc2e.interfaces.win32 import Win32Interface
    LOCAL_PLATFORM = WIN32

    SUPPORTED[WIN32] = Win32Interface
    DEFAULT_INTERFACE_TYPE = WIN32
