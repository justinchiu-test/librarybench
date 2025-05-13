import os
import time
import threading
import fnmatch
import logging
from concurrent.futures import ThreadPoolExecutor

class Watcher:
    def __init__(self, path, polling_interval=1.0):
        self.path = path
        self.polling_interval = polling_interval
        self.include_patterns = []
        self.exclude_patterns = []
        self.rate_limit_per_sec = None
        self._last_event_times = []
        self.handlers = {}  # name -> callback
        self.handler_limits = {}  # name -> (max_events_per_sec, last_reset, count)
        self.thread_pool = None
        self.logger = logging.getLogger('fs_watcher')
        self.polling_strategy = None
        self._snapshot = {}
        self._stop_event = threading.Event()
        self._thread = None
        self.batch_interval = None
        self._batch_thread = None
        self._batch_lock = threading.Lock()
        self._batch_events = []
        self._batch_enabled = False

    def configure_thread_pool(self, max_workers):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    def set_filters(self, include_patterns, exclude_patterns):
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []

    def set_throttle(self, rate_limit_per_sec):
        self.rate_limit_per_sec = rate_limit_per_sec

    def on_event(self, callback, name=None):
        handler_name = name or callback.__name__
        self.handlers[handler_name] = callback
        return handler_name

    def batch_dispatch(self, interval_ms):
        self.batch_interval = interval_ms / 1000.0
        self._batch_enabled = True
        if self._batch_thread is None:
            self._batch_thread = threading.Thread(target=self._batch_worker, daemon=True)
            self._batch_thread.start()

    def _batch_worker(self):
        while not self._stop_event.is_set():
            time.sleep(self.batch_interval)
            with self._batch_lock:
                if self._batch_events:
                    batch = list(self._batch_events)
                    self._batch_events.clear()
                else:
                    batch = []
            if batch:
                for name, callback in self.handlers.items():
                    self._dispatch_batch_to_handler(name, callback, batch)

    def configure_logging(self, level):
        self.logger.setLevel(level)

    def set_polling_strategy(self, custom_strategy):
        self.polling_strategy = custom_strategy

    def apply_rate_limit(self, handler_name, max_events_per_sec):
        self.handler_limits[handler_name] = {
            'max': max_events_per_sec,
            'last_reset': time.time(),
            'count': 0
        }

    def run_single_scan(self, path=None):
        path = path or self.path
        new_snap = self._take_snapshot(path)
        events = self._compare_snapshots(self._snapshot, new_snap)
        self._snapshot = new_snap
        for evt in events:
            self._handle_event(evt)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        # initial snapshot
        self._snapshot = self._take_snapshot(self.path)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if self._batch_thread:
            self._batch_thread.join(timeout=0.1)
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False)

    def _watch_loop(self):
        while not self._stop_event.is_set():
            time.sleep(self.polling_interval)
            try:
                new_snap = self.polling_strategy(self.path) if self.polling_strategy else self._take_snapshot(self.path)
                events = self._compare_snapshots(self._snapshot, new_snap)
                self._snapshot = new_snap
                for evt in events:
                    self._handle_event(evt)
            except Exception as e:
                self.logger.error("Error in watch loop: %s", e)

    def _take_snapshot(self, path):
        snap = {}
        for root, dirs, files in os.walk(path):
            for fname in files:
                full = os.path.join(root, fname)
                try:
                    snap[full] = os.path.getmtime(full)
                except OSError:
                    continue
        return snap

    def _compare_snapshots(self, old, new):
        events = []
        # created and modified
        for path, mtime in new.items():
            if path not in old:
                events.append(('created', path, time.time()))
            elif old[path] != mtime:
                events.append(('modified', path, time.time()))
        # deleted
        for path in old:
            if path not in new:
                events.append(('deleted', path, time.time()))
        return events

    def _handle_event(self, event):
        evt_type, path, ts = event
        if not self._filter_path(path):
            return
        # global throttle
        if self.rate_limit_per_sec:
            now = time.time()
            self._last_event_times = [t for t in self._last_event_times if now - t < 1.0]
            if len(self._last_event_times) >= self.rate_limit_per_sec:
                return
            self._last_event_times.append(now)
        data = {'type': evt_type, 'path': path, 'timestamp': ts}
        if self._batch_enabled:
            with self._batch_lock:
                self._batch_events.append(data)
        else:
            for name, callback in self.handlers.items():
                if not self._check_handler_rate(name):
                    continue
                if self.thread_pool:
                    self.thread_pool.submit(callback, data)
                else:
                    callback(data)

    def _dispatch_batch_to_handler(self, name, callback, batch):
        if not self._check_handler_rate(name, batch_size=len(batch)):
            return
        if self.thread_pool:
            self.thread_pool.submit(callback, batch)
        else:
            callback(batch)

    def _check_handler_rate(self, handler_name, batch_size=1):
        if handler_name not in self.handler_limits:
            return True
        lim = self.handler_limits[handler_name]
        now = time.time()
        if now - lim['last_reset'] >= 1.0:
            lim['last_reset'] = now
            lim['count'] = 0
        if lim['count'] + batch_size > lim['max']:
            return False
        lim['count'] += batch_size
        return True

    def _filter_path(self, path):
        basename = os.path.basename(path)
        if self.include_patterns:
            matched = any(fnmatch.fnmatch(basename, pat) for pat in self.include_patterns)
            if not matched:
                return False
        if self.exclude_patterns:
            if any(fnmatch.fnmatch(basename, pat) for pat in self.exclude_patterns):
                return False
        return True
