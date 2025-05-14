import pytest
from static_site_engine import set_output_mode, _output_mode

def test_set_output_mode_valid():
    set_output_mode("raw")
    assert _output_mode == "raw"
    set_output_mode("html")
    assert _output_mode == "html"

def test_set_output_mode_invalid():
    with pytest.raises(ValueError):
        set_output_mode("xml")
