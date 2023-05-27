"""
Ensure that coerce_to_bytearray works correctly
"""

from pyc2e.interfaces import coerce_to_bytearray


def test_coercing_to_bytearray_returns_bytearray_unchanged():
    """The function returns a bytearray unchanged"""
    original = bytearray(b"test data")
    returned = coerce_to_bytearray(original)

    assert returned is original


class TestBytesConversion:

    def test_coercing_bytes_returns_equal_bytearray(self):
        """coerce_to_bytearray returns value equal to passed bytes"""
        original = b"test"
        returned = coerce_to_bytearray(original)

        assert returned == original

    def test_coercing_bytes_returns_a_bytearray(self):
        """coerce_to_bytearray returns bytearray when passed bytes"""
        original = b"test"
        returned = coerce_to_bytearray(original)

        assert isinstance(returned, bytearray)


class TestStrConversion:

    def test_coercing_str_returns_correct_bytearray(self):
        """coerce_to_bytearray returns appropriate str conversion"""
        original = "test value"
        returned = coerce_to_bytearray(original)

        assert returned == bytearray(b"test value")

    def test_coercing_str_returns_bytearray(self):
        """coerce_to_bytearray returns bytearray if passed string"""
        original = "test value"
        returned = coerce_to_bytearray(original)

        assert isinstance(returned, bytearray)
