"""
Implementation of the shared memory interface for windows c2e games.

Uses Chris Double's reference as the main guide.
http://double.nz/creatures/developer/sharedmemory.htm

Permissions currently requested might be excessive for a client. Only intended
to support opening existing handles rather than creating new ones.

Creation may be explored in future revisions that allow imitation of the engine
to better understand original CL tools.


"""
import struct
import mmap
from typing import Union, ByteString

from pyc2e.common import (
    SCRIPT_START_STRING_REGEX,
    InterfaceException,
    ConnectFailure,
    AlreadyConnected,
    NotConnected,
    DisconnectFailure
)

from pyc2e.interfaces.response import Response
from pyc2e.interfaces.win32.win32api.events import Event
from pyc2e.interfaces.win32.win32api.mutex import Mutex
from pyc2e.interfaces.win32.win32api.process import ProcessHandle
from pyc2e.interfaces.win32.win32api.wait import (
    wait_for_multiple_objects,
    INFINITE_WAIT
)

DEFAULT_SHARED_MEMORY_SIZE = 1048576
C2E_BUFFER_HEADER = b"c2e@"

OFFSET_PID_START = 4
OFFSET_RESULT_STATUS = 8
OFFSET_DATA_SIZE_START = 12
OFFSET_RESULT_LEN = 16
OFFSET_DATA_START = 24


class BadBufferError(InterfaceException):
    """ For when the interface was acquired but it has bad memory contents"""

    def __init__(self, header_value):
        self.header_value = header_value

    def __str__(self):
        return \
            f"<BadBufferError: Expected {C2E_BUFFER_HEADER}," \
            f" but found {self.header_value}"


class ServerPIDNotFound(InterfaceException):
    pass


class Win32Interface:
    """
    Windows shared memory interface for pyc2e engine

    Currently throws away and re-acquires handles for underlying events and
    other objects. It may be possible to cache some of these rather than
    refreshing them each request. It should be investigated.

    """

    def __init__(
            self,
            game_name: str = "Docking Station",
            memory_size: int= DEFAULT_SHARED_MEMORY_SIZE,
            wait_timeout_ms: int = INFINITE_WAIT,
            require_process_access: bool= True
    ):
        """

        :param game_name: the game title to look for a shared memory entry in
        :param memory_size: how big the shared memory buffer should be
        :param wait_timeout_ms: how many milliseconds to wait for the interface
        :param require_process_access: whether we need the process
        """
        self.wait_timeout_ms = wait_timeout_ms
        self.require_process_access = require_process_access

        self.connected = False
        self._memory_size = memory_size
        self.game_name = game_name

        self.shared_memory_name = f"{self.game_name}_mem"
        self.shared_memory = None

        self.mutex_name = f"{self.game_name}_mutex"
        self.mutex_object = None

        self._result_event_name = f"{self.game_name}_result"
        self.result_event: Event = None

        self.process_id = None
        self.process_handle = None

        self._request_event_name = f"{game_name}_request"
        self.request_event: Event = None

    def connect(self) -> None:
        """Initiate a connection to the engine"""
        if self.connected:
            raise AlreadyConnected("Already connected to the engine")

        try:
            self.shared_memory = mmap.mmap(
                -1,
                self._memory_size,
                tagname=self.shared_memory_name,
                access=mmap.ACCESS_WRITE
            )
            self.mutex_object = Mutex(self.mutex_name)
            self.result_event = Event(self._result_event_name)
            self.request_event = Event(self._request_event_name)

            self.connected = True
        except Exception as e:
            raise ConnectFailure("Failed to connect to the engine") from e

    def __enter__(self):
        """generator/with-statement compatibility"""
        self.connect()
        return self

    def disconnect(self) -> None:
        """Clean up the connection to the engine"""

        if not self.connected:
            raise NotConnected("Not connected to engine")

        try:
            del self.request_event
            del self.result_event
            del self.mutex_object
            self.shared_memory.close()
            del self.shared_memory

        except Exception as e:
            raise DisconnectFailure("Failed to cleanly disconnect from the engine") from e

        self.connected = False

    def _idempotent_cleanup(self) -> None:
        if self.connected:
            self.disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._idempotent_cleanup()

    def __del__(self):
        self._idempotent_cleanup()

    # todo: do we actually need to wait for the process handle?
    def raw_request(self, query: Union[str, ByteString]) -> Response:
        """
        A raw execution request.

        :param query: the query to run.
        :return: a response object.
        """

        if not isinstance(query, ByteString):
            query = bytes(query, "latin-1")

        if not self.connected:
            self.connect()

        self.mutex_object.acquire(wait_in_ms=self.wait_timeout_ms)

        # todo: better handling of struct here
        buffer_header = self.shared_memory.read(4)
        if C2E_BUFFER_HEADER != buffer_header:
            raise BadBufferError(buffer_header)

        self.process_id = struct.unpack("I", self.shared_memory.read(4))[0]

        # write request to the buffer here!
        self.shared_memory.seek(OFFSET_DATA_START)
        self.shared_memory.write(query)
        self.shared_memory.write(b'\x00')

        # reset events
        self.result_event.reset()
        self.request_event.pulse()

        try:

            handles_to_wait_for = [
                self.result_event.handle,
                self.request_event.handle
            ]

            if self.require_process_access:
                self.process_handle = ProcessHandle(self.process_id)
                handles_to_wait_for.append(self.process_handle.handle)

            wait_for_multiple_objects(
                handles_to_wait_for,
                wait_in_ms=self.wait_timeout_ms
            )

        finally:
            if self.process_handle:
                # if it's None or Null, the c2e instance we asked for
                # by name either isn't running or isn't running in the same
                # space, for example if the game is in admin mode and the.
                # client is run as a normal user.
                self.process_handle.close()

        # copy data here
        self.shared_memory.seek(OFFSET_RESULT_STATUS)

        error, res_len, = struct.unpack("<II", self.shared_memory.read(8))

        # extract data
        self.shared_memory.seek(OFFSET_DATA_START)
        data = self.shared_memory.read(res_len)

        self.disconnect()

        return Response(
            data,
            res_len,
            bool(error)
        )

    def execute_caos(self, request_body: str) -> Response:
        """
        Attempt to run a piece of CAOS
        :param request_body:
        :return:
        """
        return self.raw_request("execute\n" + request_body)

    def test_connection(self) -> bool:
        """Tests connection to engine.

        :return: True if we can talk to an engine, false otherwise.
        """
        this_works = "this works"
        response = self.execute_caos('outs "{0}"'.format(this_works)).text
        return response.text == this_works

    def add_script(
            self,
            request_body: str,

    ) -> Response:
        """

        Attempts to add a script to the scriptorium.

        Must start with a valid script number such as 'scrp 1 1 1 1'.

        Trims the endm if it exists in the script.

        :param request_body: starts with a script header
        :return:
        """

        if not SCRIPT_START_STRING_REGEX.match(request_body):
            raise ValueError("Request does not appear to be a valid script")

        if request_body.endswith("endm"):
            request_body = request_body[:-4]

        return self.raw_request(request_body)
