import pytest

from pyc2e.interfaces.response import Response


@pytest.mark.parametrize(
    "raw_data",
    (
        b"a",
        b"a" * 128,
        bytearray(b"testing")
    )
)
class TestDataProperty:

    def test_data_gets_set(self, raw_data):
        r = Response(raw_data)
        assert r.data == raw_data

    def test_data_converted_to_bytes(self, raw_data):
        r = Response(raw_data)
        assert isinstance(r.data, bytes)


@pytest.mark.parametrize("declared_arg", (1, 2, None))
def test_declared_length_property_gets_set(declared_arg):
    r = Response(b"aa", declared_length=declared_arg)
    assert r.declared_length == declared_arg


@pytest.mark.parametrize("error_arg", (True, False, None))
def test_error_property_gets_set(error_arg):
    r = Response(b"a\0", error=error_arg)
    assert r.error == error_arg


@pytest.mark.parametrize("null_terminated_arg", (True, False))
def test_null_terminated_property_gets_set(null_terminated_arg):
    r = Response(b"a\0", null_terminated=null_terminated_arg)
    assert r.null_terminated == null_terminated_arg


class TestTextProperty:

    def test_cuts_data_when_only_declared_length_set(self):
        """Text property of Response cuts data to declared length"""
        r = Response(
            b"a" * 128,
            declared_length=5
        )
        assert r.text == "aaaaa"

    def test_cuts_correctly_when_length_and_terminator_set(self):
        """Text property of Response cuts correctly with a null terminator"""
        r = Response(
            b"aaaa\0",
            declared_length=5,
            null_terminated=True
        )
        assert r.text=="aaaa"

    def test_cuts_nothing_when_neither_length_nor_terminator_set(self):
        """Text property cuts nothing if no cutting properties are set"""
        r = Response(b"aaaaa")
        assert r.text == "aaaaa"
