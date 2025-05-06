import pytest
from IT_Manager.registry import Registry
from IT_Manager.manager import PackageManager
from IT_Manager.notifications import get_update_notifications

@pytest.fixture
def reg_updates():
    r = Registry()
    r.add_package("X", "1.0")
    r.add_package("X", "1.1")
    r.add_package("Y", "0.9")
    return r

def test_no_updates(monkeypatch, reg_updates):
    pm = PackageManager(reg_updates)
    pm.install("X", "1.1")
    pm.install("Y", "0.9")
    msgs = get_update_notifications(pm)
    assert msgs == []

def test_with_updates(reg_updates):
    pm = PackageManager(reg_updates)
    pm.install("X", "1.0")
    pm.install("Y", "0.9")
    msgs = get_update_notifications(pm)
    assert "X" in msgs[0]
    assert "1.0" in msgs[0]
    assert "1.1" in msgs[0]
    # Only X has an update
    assert len(msgs) == 1
