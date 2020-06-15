"""

An interface for connecting to c2e over a socket.

The Linux version of c2e and openc2e are the only known
server implementations that this can connect to.

"""

import socket
from typing import ByteString, Union

from pyc2e.interfaces.interface import C2eCaosInterface, StrOrByteString, coerce_to_bytearray
from pyc2e.interfaces.response import Response
from pyc2e.common import (
    NotConnected,
    DisconnectFailure,
    AlreadyConnected, ConnectFailure)

socket.setdefaulttimeout(0.200)

SOCKET_CHUNK_SIZE = 1024
LOCALHOST="127.0.0.1"


class UnixInterface(C2eCaosInterface):
    """
    An interface object that allows injection of CAOS over a socket.

    Access attempts on VirtualBox instances have gotten blank responses
    in the past despite the engine not being running.
    I think this has to do with virtualbox port forwarding. maybe
    bridged mode setup is better in the long run for lc2e stuff?
    that or ssh if we're doing password stuff
    """
    def __init__(
            self,
            port: int=20001,
            host: str="127.0.0.1",
            remote: bool=False,
            wait_timeout_ms:int =100,
            game_name: str="Docking Station"):

        super().__init__(
            wait_timeout_ms,
            game_name
        )

        self.port = port
        self.host = host
        if self.host != LOCALHOST:
            self.remote = True
        else:
            self.remote = remote
        self.socket = None

    def _connect_body(self) -> None:
        """
        Meat of the connection action, used by connect() in superclass.
        :return:
        """

        try:
            self.socket = socket.create_connection((self.host, self.port))
        except Exception as e:
            raise ConnectFailure(
                f"Failed to create socket connecting to engine at {self.host}:{self.port}"
            ) from e

    def _disconnect_body(self):
        """
        Met of disconnect method, called by connect in superclass.

        :return:
        """
        try:
            self.socket.close()

        except Exception as e:
            raise DisconnectFailure("Could not close socket when disconnecting from engine.") from e

    def raw_request(self, query: ByteString) -> Response:
        """

        Run a raw request against the c2e engine.

        Most users will not need to use this as it injects bytes  They should use execute_caos
        or add_script instead.

        :param query: the caos to run.
        :return:
        """
        if not self.connected:
            self.connect()

        final_query = coerce_to_bytearray(query)

        self.socket.send(final_query)
        self.socket.send(b"\nrscr")
        response_data = bytearray()

        done = False
        while not done:
            temp_data = self.socket.recv(SOCKET_CHUNK_SIZE)
            if len(temp_data):
                response_data.extend(temp_data)
            else:
                done = True

        self.disconnect()

        return Response(response_data)

    def execute_caos(self, request: Union[str, ByteString]) -> Response:
        caos_bytearray = coerce_to_bytearray(request)
        return self.raw_request(caos_bytearray)

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

        Doesn't perform any syntax checking. A successful script injection
        should return a Response object with blank data & text fields.

        :param script_body:
        :param family:
        :param genus:
        :param species:
        :param script_number:
        :return:
        """
        data = bytearray()
        data.extend(b"scrp %i %i %i %i\n" % (
                family,
                genus,
                species,
                script_number
            )
        )
        data.extend(coerce_to_bytearray(script_body))
        data.extend(b"\nendm")

        return self.raw_request(data)
