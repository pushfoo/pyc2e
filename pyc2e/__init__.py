"""
Top level pyc2e package.

Currently includes helpers for running the game aainst arbitrary engine names.

In the future, this may include support for config, directories, and LD_PRELOAD

"""
from .interfaces import SUPPORTED, UNIX, WIN32, DEFAULT_INTERFACE_TYPE
from .interfaces.response import Response

from .common import QueryError


def execute_caos(
    query_body: str,
    game_name: str ="Docking Station",
    timeout: int = 100
) -> Response:
    """
    Easy mode for executing CAOS against a running game.

    :param query_body: the CAOS to execute.
    :param game_name: the current name of the engine.
    :param timeout: how many ms to wait for the engine.
    :return:
    """
    interface_class = SUPPORTED[DEFAULT_INTERFACE_TYPE]

    with interface_class(
            game_name=game_name,
            wait_timeout_ms=timeout
    ) as interface:

        response = interface.execute_caos(query_body)
        return response

def add_script(
    script: str,
    game_name: str ="Docking Station",
    timeout: int = 100
) -> Response:
    """
    Add a script to the scriptorium.

    Assumes the script is headed with a valid script header.

    :param script: the script that weill be added to the scriptorium.
    :param game_name:
    :param timeout: how many ms to wait for the engine
    :return:
    """
    interface_class = SUPPORTED[DEFAULT_INTERFACE_TYPE]

    with interface_class(
            game_name=game_name,
            wait_timeout_ms=timeout
    ) as interface:
        response = interface.add_script(script)
        return response


