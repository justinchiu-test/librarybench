import pytest
from static_site_engine import url_encode, url_decode, querystring

def test_url_encode_decode():
    original = "hello world/?&="
    encoded = url_encode(original)
    assert "%" in encoded
    decoded = url_decode(encoded)
    assert decoded == original

def test_querystring_no_params():
    assert querystring("/archive") == "/archive"
    assert querystring("/archive", page=2) == "/archive?page=2"
    assert querystring("/tags", tag="python", page=3) in ("/tags?tag=python&page=3", "/tags?page=3&tag=python")
