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
from typing import ByteString

from pyc2e.common import (
    InterfaceException,
    ConnectFailure,
    DisconnectFailure
)
from pyc2e.interfaces.interface import (
    C2eCaosInterface,
    StrOrByteString,
    coerce_to_bytearray,
    generate_scrp_header
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


class Win32Interface(C2eCaosInterface):
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
        super().__init__(
            wait_timeout_ms,
            game_name
        )
        self.require_process_access = require_process_access

        self._memory_size = memory_size

        self.shared_memory_name = f"{self._game_name}_mem"
        self.shared_memory = None

        self.mutex_name = f"{self._game_name}_mutex"
        self.mutex_object = None

        self._result_event_name = f"{self._game_name}_result"
        self.result_event: Event = None

        self.process_id = None
        self.process_handle = None

        self._request_event_name = f"{self._game_name}_request"
        self.request_event: Event = None

    def _connect_body(self) -> None:
        """Initiate a connection to the engine"""

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

            self._connected = True
        except Exception as e:
            raise ConnectFailure("Failed to connect to the engine") from e

    def _disconnect_body(self) -> None:
        """Clean up the connection to the engine"""

        try:
            del self.request_event
            del self.result_event
            del self.mutex_object
            self.shared_memory.close()
            del self.shared_memory

        except Exception as e:
            raise DisconnectFailure("Failed to cleanly disconnect from the engine") from e

    # todo: do we actually need to wait for the process handle?
    def raw_request(self, query: ByteString) -> Response:
        """
        A raw execution request.

        :param query: the query to run.
        :return: a response object.
        """

        if not self.connected:
            self.connect()

        self.mutex_object.acquire(wait_in_ms=self._wait_timeout_ms)

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
                wait_in_ms=self._wait_timeout_ms
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

    def execute_caos(self, request_body: StrOrByteString) -> Response:
        """
        Attempt to run a piece of CAOS
        :param request_body:
        :return:
        """
        request_body = coerce_to_bytearray(request_body)

        return self.raw_request(b"execute\n" + request_body)

    def test_connection(self) -> bool:
        """Tests connection to engine.

        :return: True if we can talk to an engine, false otherwise.
        """
        this_works = "this works"
        response = self.execute_caos('outs "{0}"'.format(this_works)).text
        return response.text == this_works

    def add_script(
        self,
        script_body: StrOrByteString,
        family: int,
        genus: int,
        species: int,
        script_number: int
    ) -> Response:
        """
        Attempt to add a script to the scriptorium.

        The script may be a bytestring or a str, but it must be the bare
        body rather than a script headed by scrp or terminated by endm.

        Doesn't perform any syntax checking. The Response object can be
        checked for signs of errors. How errors are indicated may vary
        per platform.

        :param script_body: the body of the script
        :param family: family classifier
        :param genus: genus classifier
        :param species: species classifier
        :param script_number: script identifier
        :return:
        """
        request_data = coerce_to_bytearray(script_body)
        # prepend the script header
        request_data[:0] = generate_scrp_header(
            family, genus, species, script_number)

        return self.raw_request(request_data)
