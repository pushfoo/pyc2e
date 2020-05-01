"""
Event-related bindings for c2e
"""
import ctypes
from ctypes import WinError
from ctypes.wintypes import (
    DWORD,
    BOOL,
    LPCSTR,
    HANDLE
)

from pyc2e.interfaces.win32.win32api.common import error_if_null_return, ObjectWithHandle

EVENT_ALL_ACCESS = 0x1F0003

_open_event = ctypes.windll.kernel32.OpenEventA
_open_event.argtypes = (
    DWORD,
    BOOL,
    LPCSTR
)
_open_event.restype = HANDLE
_open_event.errcheck = error_if_null_return


def open_event(
        event_name: str,
        desired_access: int = EVENT_ALL_ACCESS,
        inherit_handle: bool = False) -> HANDLE:
    """
    Attempts to open an event object with the given name at the requested access level.

    The name must easily convert to ascii.

    :param event_name: a name to open. must be convertible to ascii
    :param desired_access:
    :param inherit_handle: whether child processes get access to the handle.
    :return: a handle for the event if successful
    """
    return _open_event(
        DWORD(desired_access),
        BOOL(inherit_handle),
        LPCSTR(bytes(event_name, 'ASCII'))
    )


reset_event = ctypes.windll.kernel32.ResetEvent
reset_event.argtypes = (HANDLE,)
reset_event.restype = BOOL
reset_event.errcheck = error_if_null_return


pulse_event = ctypes.windll.kernel32.PulseEvent
pulse_event.argtypes = (HANDLE,)
pulse_event.restype = BOOL
pulse_event.errcheck = error_if_null_return


class Event(ObjectWithHandle):
    """ Abstracts the opening of an already created event """

    def __init__(
            self,
            name: str,
            desired_access: int = EVENT_ALL_ACCESS,
            inherit_handle: bool = False
    ):
        super().__init__()
        self._handle = open_event(name, desired_access, inherit_handle)
        self.access = desired_access
        self._name = name

    @property
    def name(self):
        """Accessor, discourage changing event name once created """
        return self._name

    def reset(self) -> None:
        """ Reset the signalling of this event object"""
        if not reset_event(self.handle):
            raise WinError()

    def pulse(self) -> None:
        """Set the event to the signalling state"""
        if not pulse_event(self.handle):
            raise WinError()


