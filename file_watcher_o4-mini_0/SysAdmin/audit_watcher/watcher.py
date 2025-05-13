import asyncio
import os

from .symlink import SymlinkConfig
from .history import EventHistoryStore
from .plugins import CICDPluginManager
from .handlers import HandlerRegistry
from .filters import HiddenFileFilter
from .throttler import Throttler

class Event:
    def __init__(self, event_type, src_path, dest_path=None, is_directory=False):
        self.event_type = event_type
        self.src_path = src_path
        self.dest_path = dest_path
        self.is_directory = is_directory

    def __repr__(self):
        return f"<Event {self.event_type} {self.src_path} -> {self.dest_path}>"

    def __eq__(self, other):
        return (
            isinstance(other, Event) and
            self.event_type == other.event_type and
            self.src_path == other.src_path and
            self.dest_path == other.dest_path and
            self.is_directory == other.is_directory
        )

class Watcher:
    def __init__(
        self,
        path: str,
        symlink_config: SymlinkConfig,
        history_store: EventHistoryStore,
        plugin_manager: CICDPluginManager,
        handler_registry: HandlerRegistry,
        hidden_filter: HiddenFileFilter,
        throttler: Throttler,
        dry_run: bool = False
    ):
        self.path = path
        self.symlink_config = symlink_config
        self.history_store = history_store
        self.plugin_manager = plugin_manager
        self.handler_registry = handler_registry
        self.hidden_filter = hidden_filter
        self.throttler = throttler
        self.dry_run = dry_run

    def emit_event(self, event: Event):
        # filter hidden
        if not self.hidden_filter.filter(event):
            return False
        # throttle
        if not self.throttler.allow():
            return False
        # handlers always run
        self.handler_registry.dispatch(event)
        # plugins and history skip in dry-run
        if not self.dry_run:
            self.plugin_manager.trigger(event)
            self.history_store.write_event(event)
        return True
