"""
Holds a Response class, somewhat inspired by the requests library.
"""

from typing import ByteString, Optional


class Response:
    """
    A cross-platform abstraction of a c2e engine's interface response.

    Not meant to be instantiated by users, only by interface classes.
    The class is also intended to be immutable.

    Currently, it transparently returns the data object. In the future,
    data may be presented as a stream and act more like the requests
    library's response object.

    Optional arguments will be set to None on platforms with
    socket-based engine interfaces which do not support them.

    :param data: raw response data as provided by the engine.
    :param declared_length: (Windows only) How long the engine said the response is
    :param error: (Windows only) the error status the engine provided,
        per Chris Double's engine documentation. Other platforms must parse
        the response body to check for errors.
    :param null_terminated: whether data has a null terminator. Socket interface
        engine versions seem to omit null terminators.
    """

    def __init__(
            self,
            data: Optional[ByteString] = None,
            declared_length: Optional[int] = None,
            error: Optional[bool] = None,
            null_terminated: bool = False,
    ):

        self._data: bytes = b"" if data is None else bytes(data)

        if null_terminated and self._data and self._data[-1] != 0:
            raise ValueError(
                "Buffer does not appear to hold a null-terminated string"
            )

        self._declared_length = declared_length
        self._error = error
        self._null_terminated = null_terminated

    @property
    def data(self) -> bytes:
        """
        Blindly return the response data as the constructor got it.

        :return:
        """
        return self._data

    @property
    def declared_length(self) -> Optional[int]:
        return self._declared_length

    @property
    def text(self) -> str:
        """
        Get a text version of the buffer contents.

        This does not detect whether the response should be interpreted as
        text. It's up to the user to know that!

        The text is cut to a cutoff length. If the

        If the null terminator was specified, the last character will be
        omitted when decoding the bytes to their text representation.

        It's possible that the result may include non-printable binary,
        in which case the result will be converted to \x00 format.

        :return:
        """
        if self._declared_length is not None:
            cutoff_length = self._declared_length

        else:
            cutoff_length = len(self._data)

        if self._null_terminated:
            cutoff_length -= 1

        # under cpython slicing a bytes to its original length doesn't
        # seem to create a copy of it (ids are ==, a is b, etc), so this
        # should be efficient enough when we don't modify length.
        return self._data[:cutoff_length].decode("cp1252")

    @property
    def error(self) -> Optional[bool]:
        """
        Return error status, if any was declared by the engine.

        :return:
        """
        return self._error

    @property
    def null_terminated(self) -> Optional[bool]:
        """
        The known null termination state, if any.

        :return: whether to expect null termination on strings
        """
        return self._null_terminated
