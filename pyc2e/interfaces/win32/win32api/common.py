"""
Miscellaneous win32api support that doesn't fit anywhere else
"""
from abc import ABC
import ctypes
from ctypes import WinError
from ctypes.wintypes import BOOL, HANDLE
from typing import Any, Callable, Tuple


def error_if_null_return(retval: Any, func: Callable, args: Tuple[Any]):
    """
    Raise an error if the passed value was null, otherwise return it.

    :param retval: whatever the checked function was supposed to return
    :return:
    """
    if not retval:
        raise WinError()
    return retval


_close_handle = ctypes.windll.kernel32.CloseHandle
_close_handle.argtypes = (HANDLE, )
_close_handle.restype = BOOL


def close_handle(handle: HANDLE):
    """
    Attempt to close a passed handle. Returns True if it succeeded.

    :param handle:
    :return:
    """
    if not bool(_close_handle(handle)):
        raise WinError()


class ObjectWithHandle(ABC):
    """
    Abstract baseclass for anything that has a handle assigned to it.

    Provides default close and destructor methods.
    """
    def __init__(self):
        self._handle = None

    @property
    def handle(self):
        return self._handle

    def close(self) -> None:
        """
        Idempotently close the handle for this object

        :return:
        """
        if self._handle is None:
            return

        close_handle(self.handle)
        self._handle = None

    def __del__(self) -> None:
        """Destructor, ensuring the handle doesn't get leak on exit """
        self.close()
