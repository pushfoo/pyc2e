"""

Win32 mutex implementation and supporting functions.

Only supports opening a handle for an existing mutex rather than creating
a new one. Server functionality may arrive in future updates.

"""
import ctypes
from ctypes import wintypes
from ctypes.wintypes import BOOL, LPCSTR, DWORD

from pyc2e.interfaces.win32.win32api.common import (
    error_if_null_return,
    ObjectWithHandle
)
from pyc2e.interfaces.win32.win32api.wait import (
    INFINITE_WAIT,
    wait_for_single_object,
    WAIT_OBJECT_0
)

# TODO: do we need to have all_access, or does synchronize work fine?
MUTEX_ALL_ACCESS = 0x001F0001

_open_mutex = ctypes.windll.kernel32.OpenMutexA
_release_mutex = ctypes.windll.kernel32.ReleaseMutex

_open_mutex.argtypes = (
    DWORD,
    BOOL,
    LPCSTR
)

_open_mutex.restype = wintypes.HANDLE
_open_mutex.errcheck = error_if_null_return

_release_mutex.argtypes = (wintypes.HANDLE, )
_release_mutex.restype = wintypes.BOOL
_release_mutex.errcheck = error_if_null_return


class Mutex(ObjectWithHandle):
    """
    Wrapper around win32api mutex functionality. Only opens existing mutexes.
    """

    def __init__(self, name: str, desired_access: int = MUTEX_ALL_ACCESS):
        """
        Attempts to opens an existing mutex with the requested permissions.

        :param name: a string that can readily be converted to ASCII bytes.
        :param desired_access: a windows access permissions constant
        """
        super().__init__()  # self.handle = None
        self.name = name
        self.acquired = False
        self.access = desired_access

        self._handle = _open_mutex(
            self.access,
            0,
            wintypes.LPCSTR(bytes(self.name, 'ASCII'))
        )


    def acquire(self, wait_in_ms: int = INFINITE_WAIT):
        """
        Attempt to acquire the mutex, waiting the given amount of time

        :param wait_in_ms: how many milliseconds to wait to acquire the mutex
        :return:
        """
        if not self.acquired:
            wait_result = wait_for_single_object(self.handle, wait_in_ms)
            if wait_result is WAIT_OBJECT_0:
                self.acquired = True
            else:
                self.acquired = False
                raise ctypes.WinError()

    def __enter__(self):
        """ Pre-acquire the mutex for use in a with block"""
        self.acquire()
        return self

    def release(self) -> None:
        """Idempotently release the mutex handle"""
        if self.acquired:
            if not _release_mutex(self.handle):
                raise ctypes.WinError()

        self.acquired = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up the mutex at the end of a with block
        """
        self.release()
        self.close()

    def __del__(self) -> None:
        """
        Destructor, clean up the mutex handle
        """
        self.release()
        self.close()


