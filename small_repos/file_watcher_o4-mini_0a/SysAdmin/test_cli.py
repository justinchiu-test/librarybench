import pytest
from audit_watcher.cli import parse_args, run
from audit_watcher.watcher import Watcher

def test_parse_args_defaults():
    args = parse_args(["/path"])
    assert args.path == "/path"
    assert not args.dry_run
    assert not args.follow_symlinks
    assert args.hidden == "exclude"
    assert args.log_dir == "./logs"
    assert args.max_bytes == 1024
    assert args.backup_count == 3
    assert args.events_per_sec == 10

def test_run_configuration(tmp_path):
    logdir = str(tmp_path / "logs")
    watcher = run([
        "--dry-run",
        "--follow-symlinks",
        "--hidden", "only",
        "--log-dir", logdir,
        "--max-bytes", "123",
        "--backup-count", "5",
        "--events-per-sec", "20",
        "/watchme"
    ])
    assert isinstance(watcher, Watcher)
    assert watcher.dry_run
    assert watcher.symlink_config.follow_links
    assert watcher.hidden_filter.mode == "only"
    assert watcher.history_store.log_dir == logdir
    assert watcher.history_store.max_bytes == 123
    assert watcher.history_store.backup_count == 5
    assert watcher.throttler.limit == 20
    assert watcher.path == "/watchme"
