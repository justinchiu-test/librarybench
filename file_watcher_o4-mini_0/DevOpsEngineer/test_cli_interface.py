import pytest
from file_watcher.cli_interface import main
from file_watcher.core import SymlinkConfig

def test_cli_defaults(tmp_path, capsys):
    fw = main([])
    # defaults
    assert fw.dry_run_mode.dry_run is False
    assert fw.symlink_config == SymlinkConfig.FOLLOW
    assert fw.hidden_filter.ignore_hidden is False
    assert fw.throttler.rate == 0

def test_cli_custom_args():
    args = ['--dry-run', '--ignore-symlinks', '--ignore-hidden', '--throttle-rate', '5']
    fw = main(args)
    assert fw.dry_run_mode.dry_run is True
    assert fw.symlink_config == SymlinkConfig.IGNORE
    assert fw.hidden_filter.ignore_hidden is True
    assert fw.throttler.rate == 5
