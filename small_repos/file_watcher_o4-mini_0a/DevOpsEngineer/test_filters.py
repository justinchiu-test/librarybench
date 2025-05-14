import pytest
from file_watcher.core import HiddenFileFilter

def test_ignore_hidden_default():
    f = HiddenFileFilter()
    assert not f.allow('.secret')
    assert f.allow('visible.txt')

def test_allow_hidden_when_disabled():
    f = HiddenFileFilter(ignore_hidden=False)
    assert f.allow('.secret')
    assert f.allow('visible.txt')
