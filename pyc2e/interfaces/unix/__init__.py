"""

Nasty broken code for connecting to Linux C2e.

The same approach may work with the old OS X version if you can find it.

"""

import socket
import uuid
from tempfile import NamedTemporaryFile
from pyc2e.common import *

socket.setdefaulttimeout(0.200)

SOCKET_CHUNK_SIZE = 1024
LOCALHOST="127.0.0.1"

#TODO: make auto-sniffing of this a thing... config management
BOOTSTRAP_DIR = "/home/docking/.dockingstation/Everything Dummy"

class UnixInterface:
    """A c2e interface object representing a game"""

    '''note: this gets a blank response sometimes if engine is off...
    I think this has to do with virtualbox port forwarding. maybe
    bridged mode setup is better in the long run for lc2e stuff?
    that or ssh if we're doing password stuff...
    '''
    def __init__(
            self,
            port: int=20001,
            host: str="127.0.0.1",
            remote: bool=False,
            wait_timeout_ms:int =100,
            game_name: str="Docking Station"):
        raise NotImplementedError("This is a broken sketch")

        self.port = port
        self.host = host
        if self.host != LOCALHOST:
            self.remote = True
        else:
            self.remote = remote
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.create_connection((self.host, self.port))
        except Exception as e:
            raise ConnectFailure("Failed to create socket connecting to engine.") from e

    def __enter__(self):
        self.connect()
        return self


    def disconnect(self):
        #self.socket.shutdown(socket.SHUT_RDWR)
        try:
            self.socket.close()
        except Exception as e:
            raise DisconnectFailure("Could not close socket when disconnecting from engine.") from e


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


    def raw_request(self, caos_query):
        self.socket.send(caos_query)
        data = b""
        temp_data = None
        done = False
        while not done:
            temp_data = self.socket.recv(SOCKET_CHUNK_SIZE)
            if len(temp_data):
                data += temp_data
            else:
                done = True
        return data

    def caos_request(self, request):
        return self.raw_request(request + b"\nrscr")


    def inject_request(self, request_body):
        """
        Uses file injection as a work-around for a possible issue with the
        btetwork interface. Needs to be investigated more thoroughly.

        :param request_body:
        :return:
        """
        if self.remote:
            raise NotImplementedError("scrp injection on remote targets not yet supported")
        if not request_body.startswith("scrp"):
            raise ValueError("Expected 'scrp' at start of script injection")
        engine_response = None

        #need to figure out where the to load tempfiles from
        try:
            with NamedTemporaryFile(suffix=".cos",
                                    prefix="JECTTMP_",
                                    dir=BOOTSTRAP_DIR) as temp_cos_file:
                temp_cos_file.write(request_body)

                engine_response = self.caos_request(
                    'ject "{0}" 2'.format(temp_cos_file.name).encode())
        except Exception as e:
            raise QueryError("Experienced a problem running the query") from e

        return engine_response
