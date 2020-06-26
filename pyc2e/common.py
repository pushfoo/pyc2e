"""
    Common classes used by Windows and *NIX c2e interfaces.
"""


class InterfaceException(Exception):
    """Base c2e interface error."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "<C2eInterfaceException: '%s'>" % self.message


class ConnectFailure(InterfaceException):
    """
    Base class for setup failures when trying to initialize interface.
    """
    pass


class DisconnectFailure(InterfaceException):
    """
    Base class for setup failures when tearing down an interface.
    """
    pass


class InputTooLong(InterfaceException):
    """
    Request sent is longer than can be handled by the interface.
    """
    def __init__(self, message):
        self.message=message


class AlreadyConnected(InterfaceException):
    """
    Indicates that the interface is already in a connected state.
    """
    pass


class NotConnected(InterfaceException):
    """
    We're not connected to the engine and can't run!
    """
    pass


class QueryError(InterfaceException):
    """
    The connection seemed to go fine, but something went wrong
    with running the query.
    """
    pass
