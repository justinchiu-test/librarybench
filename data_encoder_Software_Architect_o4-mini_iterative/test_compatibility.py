import pytest
from compatibility import ensure_backward_compatibility, parse_version

@pytest.mark.parametrize("current, previous, expected", [
    ("1.0.0", "1.0.0", True),    # identical versions
    ("1.2.5", "1.2.3", True),    # patch bump
    ("1.3.0", "1.2.9", True),    # minor bump
    ("1.3.0", "1.3.0", True),    # identical again
    ("1.3.1", "1.3.2", False),   # patch decreased
    ("1.2.0", "1.3.0", False),   # minor decreased
    ("2.0.0", "1.5.9", False),   # major changed
    ("1.0",   "1.0.0", True),    # shorthand versions
    ("1.0.1", "1.0",   True),
    ("1.0",   "1.0.1", False),
])
def test_ensure_backward_compatibility(current, previous, expected):
    assert ensure_backward_compatibility(current, previous) == expected

def test_parse_version_standard():
    assert parse_version("2.5.3") == (2, 5, 3)

def test_parse_version_shorthand():
    assert parse_version("4.7")   == (4, 7, 0)
    assert parse_version("9")     == (9, 0, 0)

def test_parse_version_invalid():
    with pytest.raises(ValueError):
        parse_version("a.b.c")
    with pytest.raises(ValueError):
        parse_version("1.two.3")
