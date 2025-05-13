import argparse
from .symlink import SymlinkConfig
from .history import EventHistoryStore
from .plugins import CICDPluginManager
from .handlers import HandlerRegistry
from .filters import HiddenFileFilter
from .throttler import Throttler
from .watcher import Watcher

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Audit filesystem changes")
    parser.add_argument("path", help="Path to watch")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks")
    parser.add_argument("--hidden", choices=("exclude", "only", "all"), default="exclude", help="Hidden files policy")
    parser.add_argument("--log-dir", default="./logs", help="Directory for event logs")
    parser.add_argument("--max-bytes", type=int, default=1024, help="Max bytes per log file before rotation")
    parser.add_argument("--backup-count", type=int, default=3, help="Number of rotated backups")
    parser.add_argument("--events-per-sec", type=int, default=10, help="Throttling: events per second limit")
    return parser.parse_args(args)

def run(args=None):
    ns = parse_args(args)
    syc = SymlinkConfig(ns.follow_symlinks)
    history = EventHistoryStore(ns.log_dir, ns.max_bytes, ns.backup_count)
    plugins = CICDPluginManager()
    handlers = HandlerRegistry()
    hidden = HiddenFileFilter(ns.hidden)
    throttler = Throttler(ns.events_per_sec)
    watcher = Watcher(ns.path, syc, history, plugins, handlers, hidden, throttler, dry_run=ns.dry_run)
    return watcher
