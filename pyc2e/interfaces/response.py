from typing import ByteString


class Response:
    """
    A response from a c2e engine.

    Not meant to be instantiatyed by users, only interface classes.

    Currently transparently returns the data object.
    In the future, data may be presented as a stream and act more like the
    requests library.

    """

    def __init__(
            self,
            data: ByteString = None,
            expected_length: int = None,
            error: bool = None):
        """

        Data is a bytestring data source. Right now, this is passive and only
        prevents people from trying to set data.

        Windows-only properties include:

        Error is a windows-only property that corresponds to chris double's
        error flag documentation. Other platforms will

        expected_length, how long the response should be

        :param data:
        :param expected_length:
        :param error:
        """
        self._expected_length = expected_length
        self._data: ByteString = data or b""
        self._error = error

    @property
    def data(self):
        """
        Blindly return the data of the response.

        :return:
        """
        return self._data

    @property
    def text(self):
        """
        Get a text version of the buffer contents.

        It's possible that the result may include non-printable binary,
        in which case the result will be converted to \x00 format.

        :return:
        """

        if not self._data[-1] == 0:
            raise ValueError(
                "Buffer does not appear to hold a null-terminated string")

        return self._data[:self._expected_length-1].decode("latin-1")

    @property
    def error(self):
        """
        Return error status, if any exists.
        :return:
        """
        return self._error




