import pytest
from audit_watcher.filters import HiddenFileFilter
from audit_watcher.watcher import Event

def test_filter_exclude():
    flt = HiddenFileFilter("exclude")
    e1 = Event("modify", "/tmp/.secret")
    e2 = Event("modify", "/tmp/visible")
    assert not flt.filter(e1)
    assert flt.filter(e2)

def test_filter_only():
    flt = HiddenFileFilter("only")
    e1 = Event("modify", "/tmp/.secret")
    e2 = Event("modify", "/tmp/visible")
    assert flt.filter(e1)
    assert not flt.filter(e2)

def test_filter_all():
    flt = HiddenFileFilter("all")
    e1 = Event("modify", "/tmp/.secret")
    e2 = Event("modify", "/tmp/visible")
    assert flt.filter(e1)
    assert flt.filter(e2)

def test_invalid_mode():
    with pytest.raises(ValueError):
        HiddenFileFilter("invalid")
