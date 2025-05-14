import sys
import pytest
from watcher.cli_interface import main
from watcher.cli_interface import Watcher as CLIWatcher

def test_cli_parsing(tmp_path, monkeypatch):
    tmp = tmp_path / 'dir'
    tmp.mkdir()
    args = [
        'prog', str(tmp),
        '--dry-run', '--no-symlinks',
        '--debounce', '0.2', '--poll', '0.3',
        '--max-retries', '2', '--retry-delay', '0.05',
        '--no-hidden-filter'
    ]
    monkeypatch.setattr(sys, 'argv', args)
    called = []
    def fake_start(self):
        called.append(self)
    monkeypatch.setattr(CLIWatcher, 'start', fake_start)
    main()
    watcher = called[0]
    assert watcher.dry_run
    assert not watcher.follow_symlinks
    assert watcher.debounce_interval == 0.2
    assert watcher.poll_interval == 0.3
    assert watcher.max_retries == 2
    assert watcher.retry_delay == 0.05
    assert not watcher.hidden_filter
