import pytest
from osscli.hooks import register_hook, get_hooks
def dummy(): pass
def test_register_and_get_hooks():
    register_hook("test", dummy, when="pre")
    register_hook("test", dummy, when="post")
    pre = get_hooks("pre")
    post = get_hooks("post")
    assert "test" in pre and dummy in pre["test"]
    assert "test" in post and dummy in post["test"]
def test_invalid_when():
    with pytest.raises(ValueError):
        register_hook("x", dummy, when="mid")
