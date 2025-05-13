import os
import time
import threading
import logging
import fnmatch
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import namedtuple

Event = namedtuple('Event', ['event_type', 'src_path', 'timestamp'])

class FileWatcher:
    def __init__(self):
        self.executor = None
        self.worker_count = 0
        self.include = []
        self.exclude = []
        self.max_events = None
        self.per_ms = None
        self.callback = None
        self.batch_time_ms = None
        self.logger = None
        self.polling_strategy = None
        self.rate_limits = {}
        self.running = False
        self._batch_lock = threading.Lock()
        self._batch = []
        self._last_dispatch = 0

    def configure_thread_pool(self, worker_count):
        if self.executor:
            self.executor.shutdown(wait=False)
        self.worker_count = worker_count
        self.executor = ThreadPoolExecutor(max_workers=worker_count)

    def set_filters(self, include=None, exclude=None):
        self.include = include or []
        self.exclude = exclude or []

    def set_throttle(self, max_events, per_ms):
        self.max_events = max_events
        self.per_ms = per_ms

    def on_event(self, reload_callback):
        self.callback = reload_callback

    def batch_dispatch(self, batch_time_ms):
        self.batch_time_ms = batch_time_ms

    def configure_logging(self, level):
        self.logger = logging.getLogger('FileWatcher')
        self.logger.setLevel(level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_polling_strategy(self, custom_fs_scanner):
        self.polling_strategy = custom_fs_scanner

    def apply_rate_limit(self, key, limit):
        self.rate_limits[key] = limit

    def run_single_scan(self, path):
        root = Path(path)
        matched = set()
        for pattern in self.include:
            for p in root.rglob(pattern.replace('**/', '')):
                if p.is_file():
                    rel = str(p)
                    matched.add(rel)
        # apply exclude
        result = []
        for f in matched:
            excluded = False
            for pat in self.exclude:
                if fnmatch.fnmatch(f, pat):
                    excluded = True
                    break
            if not excluded:
                result.append(f)
        return sorted(result)

    def start(self):
        self.running = True
        if self.logger:
            self.logger.debug("Watcher started")

    def stop(self):
        self.running = False
        if self.logger:
            self.logger.debug("Watcher stopped")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()

    def _emit_event(self, event_type, src_path):
        evt = Event(event_type=event_type, src_path=src_path, timestamp=time.time())
        if self.batch_time_ms:
            with self._batch_lock:
                self._batch.append(evt)
                now = time.time() * 1000
                if now - self._last_dispatch >= self.batch_time_ms:
                    batch = list(self._batch)
                    self._batch.clear()
                    self._last_dispatch = now
                    self._dispatch(batch)
        else:
            self._dispatch(evt)

    def _dispatch(self, evt):
        if not self.callback:
            return
        if isinstance(evt, list):
            for e in evt:
                self._submit(e)
        else:
            self._submit(evt)

    def _submit(self, evt):
        if self.executor:
            self.executor.submit(self.callback, evt)
        else:
            # synchronous fallback
            self.callback(evt)

# Singleton instance and module-level API
_watcher = FileWatcher()

def configure_thread_pool(worker_count):
    _watcher.configure_thread_pool(worker_count)

def set_filters(include=None, exclude=None):
    _watcher.set_filters(include, exclude)

def set_throttle(max_events, per_ms):
    _watcher.set_throttle(max_events, per_ms)

def on_event(reload_callback):
    _watcher.on_event(reload_callback)

def batch_dispatch(batch_time_ms):
    _watcher.batch_dispatch(batch_time_ms)

def configure_logging(level):
    _watcher.configure_logging(level)

def set_polling_strategy(custom_fs_scanner):
    _watcher.set_polling_strategy(custom_fs_scanner)

def apply_rate_limit(key, limit):
    _watcher.apply_rate_limit(key, limit)

def run_single_scan(path):
    return _watcher.run_single_scan(path)

def get_watcher():
    return _watcher
