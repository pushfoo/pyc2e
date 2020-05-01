import ctypes
from ctypes.wintypes import HANDLE, BOOL, DWORD
from .common import ObjectWithHandle, error_if_null_return

PROCESS_ALL_ACCESS = 2035711

_open_process = ctypes.windll.kernel32.OpenProcess
_open_process.argtypes = (
    DWORD,
    BOOL,
    DWORD
)
_open_process.restype = HANDLE
_open_process.errcheck = error_if_null_return


class ProcessHandle(ObjectWithHandle):

    def __init__(
            self,
            process_id: int,
            inherit_handle: bool = False,
            desired_access: int = PROCESS_ALL_ACCESS
    ):
        """
        Attempt to open a handle for the given PID with requested access level.

        Raises a WinError if it fails.

        see msdn doc for OpenProcess for more information about process handles.

        :param process_id: the id of the process to open
        :param inherit_handle: whether children should inherit permissions
        :param desired_access: a windows flag specifying

        """
        super().__init__()
        self._id = process_id
        self._inherit_handle = inherit_handle
        self._desired_access = PROCESS_ALL_ACCESS

        self._handle = _open_process(
            DWORD(desired_access),
            BOOL(inherit_handle),
            DWORD(process_id)
        )

        @property
        def pid(self) -> int:
            return self._id








