"""

An interface for connecting to c2e over a socket.

The Linux version of c2e and openc2e are the only known
server implementations that this can connect to.

"""

import socket
from typing import ByteString, Union

from pyc2e.interfaces.response import Response
from pyc2e.common import (
    NotConnected,
    DisconnectFailure,
    AlreadyConnected, ConnectFailure)

socket.setdefaulttimeout(0.200)

SOCKET_CHUNK_SIZE = 1024
LOCALHOST="127.0.0.1"


class UnixInterface:
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

        self.connected = False

        self.port = port
        self.host = host
        if self.host != LOCALHOST:
            self.remote = True
        else:
            self.remote = remote
        self.socket = None

    def connect(self):
        if self.connected:
            raise AlreadyConnected("Already connected to the engine")

        try:
            self.socket = socket.create_connection((self.host, self.port))
        except Exception as e:
            raise ConnectFailure(
                f"Failed to create socket connecting to engine at {self.host}:{self.port}"
            ) from e

        self.connected = True

    def __enter__(self):
        self.connect()
        return self

    def disconnect(self):

        if not self.connected:
            raise NotConnected("Not connected to engine")

        try:
            self.socket.close()

        except Exception as e:
            raise DisconnectFailure("Could not close socket when disconnecting from engine.") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def raw_request(self, caos_query: Union[str, ByteString]) -> Response:
        """
        Run a raw request against the c2e engine.

        :param caos_query: the caos to run.
        :return:
        """
        if not self.connected:
            self.connect()

        if isinstance(caos_query, ByteString):
            final_query = caos_query
        else:
            final_query = caos_query.encode("latin-1")

        self.socket.send(final_query)
        self.socket.send(b"\nrscr")
        data = bytearray()

        done = False
        while not done:
            temp_data = self.socket.recv(SOCKET_CHUNK_SIZE)
            if len(temp_data):
                data.extend(temp_data)
            else:
                done = True

        self.disconnect()

        return Response(data)

    def execute_caos(self, request: Union[str, ByteString]) -> Response:
        return self.raw_request(request)


    def add_script(self, request_body: Union[str, ByteString]) -> Response:
        """
        Attempt to add a script to the scriptorium.

        :param request_body: the body to add, including the scrp header
        :return:
        """
        self.raw_request(request_body)



