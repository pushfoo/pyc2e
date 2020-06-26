"""
Test that comment stripping is working correctly.
"""
from io import StringIO
from pyc2e.miniparser import read_and_strip_comments


def test_strips_comments():
    src_with_comments = \
    """
    * start of caos file, this should end up being a blank line
    outs "test"
    scrp 1 1 1 1
        * some stuff happens here?
        outs "script body"
    endm*badly placed comment
"""
    expected = \
    """
    
    outs "test"
    scrp 1 1 1 1
        
        outs "script body"
    endm
"""
    stripped = read_and_strip_comments(StringIO(src_with_comments))

    assert stripped.encode('unicode-escape') == expected.encode('unicode-escape')
