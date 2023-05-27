"""
Top level pyc2e package.

This currently limited to helpers for running the game
against arbitrary engine names.

In the future, this may include support for config, directories,
and LD_PRELOAD.
"""
from pyc2e.interfaces import (
    DEFAULT_INTERFACE_TYPE,
    SUPPORTED,
    WIN32,
    UnixInterface,
)
if WIN32 in SUPPORTED:
    from pyc2e.interfaces import Win32Interface

from pyc2e.interfaces.response import Response


def execute_caos(
    query_body: str,
    game_name: str = "Docking Station",
    timeout: int = 100
) -> Response:
    """
    Easy mode for executing CAOS against a running game.

    :param query_body: The CAOS to execute.
    :param game_name: The current name of the engine.
    :param timeout: How many ms to wait for the engine's response
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
    game_name: str = "Docking Station",
    timeout: int = 100
) -> Response:
    """
    Add a script to the scriptorium.

    Assumes the script is headed with a valid script header.

    :param script: The script to add to the scriptorium.
    :param game_name: The engine instance's self-reported name
    :param timeout: How many ms to wait for the engine's response
    :return:
    """
    interface_class = SUPPORTED[DEFAULT_INTERFACE_TYPE]

    with interface_class(
            game_name=game_name,
            wait_timeout_ms=timeout
    ) as interface:
        response = interface.add_script(script)
        return response


__all__ = [
    "DEFAULT_INTERFACE_TYPE",
    "add_script",
    "execute_caos",
    "SUPPORTED",
    "UnixInterface",
    "Win32Interface",
]
