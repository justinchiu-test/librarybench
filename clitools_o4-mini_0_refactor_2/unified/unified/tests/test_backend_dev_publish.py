import pytest
from adapters.backend_dev.microcli.publish import publish_package

def test_publish_default():
    assert publish_package()

def test_publish_custom():
    assert publish_package("http://example.com")

def test_publish_invalid():
    with pytest.raises(ValueError):
        publish_package("not a url")