"""
Baseclass and common functionality for c2e interfaces.
"""

from abc import ABC, abstractmethod
from collections import ByteString
from typing import Union

from pyc2e.interfaces.response import Response

from pyc2e.common import (
    NotConnected,
    AlreadyConnected
)


StrOrByteString = Union[str, ByteString]


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

    def __init__(
        self,
        wait_timeout_ms: int=100,
        game_name: str="Docking Station"
    ):
        self._connected = False
        self._wait_timeout_ms = wait_timeout_ms
        self._game_name = game_name

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
        self.disconnect()
        self._connected = False

    @abstractmethod
    def raw_request(self, caos_query: ByteString) -> Response:
        """

        :param caos_query:
        :return:
        """
        pass

    @abstractmethod
    def execute_caos(self, caos_query: StrOrByteString) -> Response:
        """
        Run a piece of CAOS without storing it, returning the result.

        If it is a string, it will be converted to bytes before execution.

        The response object will contain a string of any output created
        during the request.

        If you want to add scripts to the scriptorium, you are looking for
        add_script instead.

        :param caos_query: valid CAOS to attempt running.
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

        :param script_body:
        :param family:
        :param genus:
        :param species:
        :param script_number:
        :return:
        """
        pass






