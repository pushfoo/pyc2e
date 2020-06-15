"""
Baseclass and common functionality for c2e interfaces.
"""

from abc import ABC, abstractmethod
from typing import Union, ByteString

from pyc2e.interfaces.response import Response

from pyc2e.common import (
    NotConnected,
    AlreadyConnected
)


StrOrByteString = Union[str, ByteString]


def coerce_to_bytearray(source: StrOrByteString):
    """
    Coerce the source to a bytearray or return it if it already is one.

    Encodes using latin-1 to start with.

    :param source: a str, bytes, or bytearray to ensure is a bytearray
    :return:
    """
    if isinstance(source, bytearray):
        return source
    elif isinstance(source, bytes):
        return bytearray(source)

    return bytearray(source.encode("latin-1"))


class C2eCaosInterface(ABC):
    """
    Baseclass for engine CAOS interfaces.

    Implementations should implement the following methods:
    * _connect_body
    * _disconnect_body
    * raw_request
    * execute_caos
    * add_script

    """

    def __init__(self, wait_timeout_ms: int, game_name: str):
        self._connected: bool = False
        self._wait_timeout_ms: int = wait_timeout_ms
        self._game_name: str = game_name

    @property
    def connected(self) -> bool:
        """
        Whether or not the interface is connected or not

        :return:
        """
        return self._connected

    @abstractmethod
    def _connect_body(self) -> None:
        """
        Perform the bulk of the connection to the engine

        Should be implemented by subclasses.
        """
        pass

    def connect(self):
        """
        Connects to the game engine,
        :return:
        """
        if self._connected:
            raise AlreadyConnected("Already connected to the engine")

        self._connect_body()
        self._connected = True

    def __enter__(self):
        self.connect()
        return self

    @abstractmethod
    def _disconnect_body(self) -> None:
        """
        Perform the bulk of disconnecting from the engine.

        Subclasses should implement this.

        :return:
        """
        pass

    def disconnect(self) -> None:
        if not self._connected:
            raise NotConnected("Not connected to engine")

        self._disconnect_body()

        self._connected = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connected:
            self.disconnect()

        self._connected = False

    def __del__(self):
        """
        Destructor, cleans up any lingering connections.

        :return:
        """
        if self.connected:
            self.disconnect()

    @abstractmethod
    def raw_request(self, query: ByteString) -> Response:
        """
        Injects the given bytestring into the engine interface.

        Most users won't need to use this function or care about it.

        They should use execute_caos and add_script instead.

        :param query: the query to inject into the engine.
        :return:
        """
        pass

    @abstractmethod
    def execute_caos(self, caos_to_execute: StrOrByteString) -> Response:
        """
        Run a piece of CAOS without storing it, returning the result.

        If it is a string, it will be converted to bytes before execution.

        The response object will contain a string of any output created
        during the request.

        If you want to add scripts to the scriptorium, you are looking for
        add_script instead.

        :param caos_to_execute: valid CAOS to attempt running.
        :return:
        """
        pass

    @abstractmethod
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
        pass






