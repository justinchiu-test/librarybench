import pytest
import os
from Frontend_Developer.package_manager.registry import Registry
from Frontend_Developer.package_manager.manager import PackageManager

@pytest.fixture
def registry(tmp_path):
    return Registry()

@pytest.fixture
def manager(registry):
    return PackageManager(registry)

def test_pin_and_list(registry, manager):
    manager.pin("packageA", "1.0.0")
    pins = manager.list_pins()
    assert pins == {"packageA": "1.0.0"}

    # pin another package
    manager.pin("packageB", "2.0.0")
    pins2 = manager.list_pins()
    assert pins2 == {"packageA": "1.0.0", "packageB": "2.0.0"}

def test_pin_invalid(registry, manager):
    with pytest.raises(ValueError):
        manager.pin("packageA", "9.9.9")

def test_unpin(registry, manager):
    manager.pin("packageA", "1.0.0")
    manager.unpin("packageA")
    assert manager.list_pins() == {}
    # unpin non-existent is silent
    manager.unpin("packageA")  # no error

def test_update_success(registry, manager):
    manager.pin("packageA", "1.0.0")
    manager.update("packageA", "2.0.0")
    assert manager.list_pins()["packageA"] == "2.0.0"

def test_update_not_pinned(registry, manager):
    with pytest.raises(KeyError):
        manager.update("packageA", "1.0.0")

def test_save_and_load(tmp_path, registry, manager):
    # pin some
    manager.pin("packageA", "1.1.0")
    manager.pin("packageB", "2.0.0")
    file = tmp_path / "pins.txt"
    manager.save_pins(str(file))

    # new manager
    m2 = PackageManager(registry)
    m2.load_pins(str(file))
    assert m2.list_pins() == manager.list_pins()

def test_load_invalid_format(tmp_path, registry):
    file = tmp_path / "bad.txt"
    file.write_text("badline\npkgwithoutversion\npackageA==9.9.9\n")
    m = PackageManager(registry)
    with pytest.raises(ValueError):
        m.load_pins(str(file))

def test_save_empty(tmp_path, registry):
    m = PackageManager(registry)
    file = tmp_path / "empty.txt"
    m.save_pins(str(file))
    content = file.read_text()
    assert content == ""
