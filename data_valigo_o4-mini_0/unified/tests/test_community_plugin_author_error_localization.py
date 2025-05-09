import pytest
from community_plugin_author.validator.errors import ErrorLocalizer

def test_default_translate():
    loc = ErrorLocalizer()
    assert loc.translate("hello") == "hello"

def test_register_and_translate():
    loc = ErrorLocalizer()
    loc.register('es', lambda m: f"ES:{m}")
    assert loc.translate("hi", 'es') == "ES:hi"
    # fallback to default
    assert loc.translate("hi", 'fr') == "hi"
