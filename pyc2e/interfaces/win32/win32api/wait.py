"""
Wait-related functions for handling multiple  for multiple things.

Todo: abstract waiting further to neatly wrap info from the wait API
https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitformultipleobjects

"""
import ctypes
from ctypes import POINTER
from ctypes.wintypes import HANDLE, DWORD, BOOL
from typing import List

INFINITE_WAIT = -1
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
WAIT_OBJECT_0 = 0x0000000

wait_for_single_object = ctypes.windll.kernel32.WaitForSingleObject
wait_for_single_object.argtypes = (
    HANDLE,
    DWORD)
wait_for_single_object.restype = DWORD

_wait_for_multiple_objects = ctypes.windll.kernel32.WaitForMultipleObjects
_wait_for_multiple_objects.argtypes = (
    DWORD,
    POINTER(HANDLE),
    BOOL,
    DWORD)
_wait_for_multiple_objects.restype = DWORD


def wait_for_multiple_objects(
        handle_array: List[HANDLE],
        wait_all: bool = False,
        wait_in_ms: int =0
) -> int:
    """
    Wait for multiple win32api objects.

    wait_all is whether all objects are required to signal an event

    See Microsoft's documentation for more information:
    https://docs.microsoft.com/en-us/windows/win32api/sync/waiting-for-multiple-objects
    https://docs.microsoft.com/en-us/windows/win32api/api/synchapi/nf-synchapi-waitformultipleobjects

    :param handle_array: an array of win32api object handles
    :param wait_all: whether to require all events to signal a status
    :param wait_in_ms:
    :return:
    """

    number_of_handles = len(handle_array)

    # seems correct despite PyCharm's type checking saying ints aren't callable
    handle_pointer_array = (HANDLE * number_of_handles)()
    for handle_index, handle in enumerate(handle_array):
        handle_pointer_array[handle_index] = handle_array[handle_index]

    return _wait_for_multiple_objects(
        number_of_handles,
        handle_pointer_array,
        wait_all,
        wait_in_ms
    )

