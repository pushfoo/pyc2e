"""
Holds a Response class, somewhat inspired by the requests library.

It doesn't yet imitate that library very well.
"""

from typing import ByteString, Union


class Response:
    """
    A cross-platform abstraction of a c2e engine's interface response.

    Not meant to be instantiated by users, only by interface classes.

    All attributes are hidden behind properties. The class is not meant to
    be altered once created.

    Currently, it transparently returns the data object. In the future,
    data may be presented as a stream and act more like the requests
    library's response object.
    """

    def __init__(
            self,
            data: ByteString = None,
            declared_length: int = None,
            error: bool = None,
            null_terminated: bool = False,
    ):
        """

        Build a cross-platform response object.

        Data is a bytestring data source. It will be converted to bytes.

        Windows-only properties include:

        declared_length, how long the engine said the response will be.
        None on socket interface platforms.

        error, a windows-only property that corresponds to chris
        double's error flag documentation. Programs using the socket
        interface will have to parse the body of the response to decide if
        there was an error condition.

        null_terminator, whether to expect a null terminator at the end if
        the response should be a string. The socket interface appears to
        omit null terminators.

        :param data: raw response data as provided by the engine.
        :param declared_length: How long the engine said the response is
        :param error: the error status the engine provided, if any.
        :param null_terminated: whether data has a null terminator
        """

        if null_terminated and data[-1] != 0:
            raise ValueError(
                "Buffer does not appear to hold a null-terminated string"
            )

        if data is None:
            self._data = b""
        else:
            self._data: bytes = bytes(data)

        self._declared_length: int = declared_length
        self._error: bool = error
        self._null_terminated: bool = null_terminated

    @property
    def data(self) -> bytes:
        """
        Blindly return the response data as the constructor got it.

        :return:
        """
        return self._data

    @property
    def declared_length(self) -> int:
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
    def error(self) -> Union[bool, None]:
        """
        Return error status, if any was declared by the engine.

        :return:
        """
        return self._error

    @property
    def null_terminated(self) -> bool:
        """
        If the return data is a string, whether it will be null terminated

        :return: whether to expect null termination on strings
        """
        return self._null_terminated
