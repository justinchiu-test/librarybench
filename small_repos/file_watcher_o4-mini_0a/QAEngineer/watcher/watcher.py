import asyncio
import os
import time
import errno

from .history_store import HistoryStore

class Watcher:
    def __init__(self, paths, *, dry_run=False, follow_symlinks=True,
                 debounce_interval=0.5, poll_interval=1.0,
                 max_retries=3, retry_delay=0.1, hidden_filter=True):
        self.paths = paths
        self.dry_run = dry_run
        self.follow_symlinks = follow_symlinks
        self.debounce_interval = debounce_interval
        self.poll_interval = poll_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.hidden_filter = hidden_filter

        self.history = HistoryStore()
        self.handlers = {'create': [], 'modify': [], 'delete': []}
        self.plugins = []

        # Initialize debounce tracking and take the initial snapshot
        self._last_event_time = {}
        self._last_snapshot = self._take_snapshot()

    def register_handler(self, event_type, callback):
        if event_type in self.handlers:
            self.handlers[event_type].append(callback)

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def _take_snapshot(self):
        snap = {}
        for root in self.paths:
            for dirpath, dirnames, filenames in os.walk(
                    root, followlinks=self.follow_symlinks):
                for name in filenames:
                    path = os.path.join(dirpath, name)
                    try:
                        stat = os.stat(path, follow_symlinks=self.follow_symlinks)
                        snap[path] = stat.st_mtime
                    except FileNotFoundError:
                        continue
        return snap

    def _detect_changes(self, old, new):
        events = []
        old_paths = set(old.keys())
        new_paths = set(new.keys())
        created = new_paths - old_paths
        deleted = old_paths - new_paths
        common = old_paths & new_paths
        modified = {p for p in common if new[p] > old[p]}

        for p in created:
            events.append((p, 'create'))
        for p in modified:
            events.append((p, 'modify'))
        for p in deleted:
            events.append((p, 'delete'))
        return events

    def _filter_event(self, path):
        name = os.path.basename(path)
        if self.hidden_filter and (name.startswith('.') or name.endswith('~')):
            return False
        return True

    def _should_handle(self, path, event):
        now = time.time()
        key = (path, event)
        last = self._last_event_time.get(key, 0)
        if now - last < self.debounce_interval:
            return False
        self._last_event_time[key] = now
        return True

    async def watch(self):
        # Use the snapshot taken at initialization
        while True:
            try:
                await asyncio.sleep(self.poll_interval)
                new_snap = self._take_snapshot()
                events = self._detect_changes(self._last_snapshot, new_snap)
                self._last_snapshot = new_snap
                for path, event in events:
                    if not self._filter_event(path):
                        continue
                    if not self._should_handle(path, event):
                        continue
                    # record in history
                    self.history.add(path, event)
                    # notify plugins
                    for plugin in self.plugins:
                        plugin.on_event(path, event)
                    # invoke handlers with retry logic
                    for handler in self.handlers.get(event, []):
                        async def call_handler(cb=handler, p=path, e=event):
                            retries = 0
                            while True:
                                try:
                                    result = cb(p, e)
                                    if asyncio.iscoroutine(result):
                                        await result
                                    break
                                except (PermissionError, OSError):
                                    if retries < self.max_retries:
                                        retries += 1
                                        await asyncio.sleep(self.retry_delay)
                                        continue
                                    else:
                                        break
                        asyncio.create_task(call_handler())
            except asyncio.CancelledError:
                break

    def start(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.watch())
        except KeyboardInterrupt:
            pass
