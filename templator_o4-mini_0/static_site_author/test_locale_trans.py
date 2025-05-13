import pytest
from static_site_engine import set_locale, trans

def test_default_locale():
    # default is English, returns key
    assert trans("hello") == "hello"

def test_set_locale_and_trans():
    set_locale("es")
    assert trans("hello") == "hola"
    assert trans("goodbye") == "adios"
    assert trans("unknown") == "unknown"
    set_locale("de")
    assert trans("hello") == "hallo"
    assert trans("goodbye") == "auf wiedersehen"
