import pytest
from static_site_engine import trim_whitespace

def test_trim_whitespace_basic():
    text = "line1   \n\n\nline2\t\n\nline3\n"
    trimmed = trim_whitespace(text)
    # No trailing spaces
    assert "   \n" not in trimmed
    # At most two consecutive newlines
    assert "\n\n\n" not in trimmed
    assert trimmed.endswith("line3")
