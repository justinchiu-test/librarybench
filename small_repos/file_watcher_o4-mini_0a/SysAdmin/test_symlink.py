import pytest
from audit_watcher.symlink import SymlinkConfig

def test_default_symlink_config():
    cfg = SymlinkConfig()
    assert not cfg.follow_links

def test_custom_symlink_config():
    cfg = SymlinkConfig(follow_links=True)
    assert cfg.follow_links
