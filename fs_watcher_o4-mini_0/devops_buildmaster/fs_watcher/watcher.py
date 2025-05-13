import os
import time
import threading
import logging
from fnmatch import fnmatch
from concurrent.futures import ThreadPoolExecutor
from collections import deque

class Watcher:
    def __init__(self):
        self._max_workers = None
        self._executor = None
        self._include = []
        self._exclude = []
        self._throttle_limit = None
        self._throttle_window = None
        self._throttle_times = deque()
        self._callbacks = []
        self._batch_interval = None
        self._batch_thread = None
        self._batch_lock = threading.Lock()
        self._batch_queue = []
        self._batch_event = threading.Event()
        self._logger = logging.getLogger(__name__)
        self._polling_strategy = None
        self._rate_limits = {}
        self._running = False

    def configure_thread_pool(self, max_workers):
        self._max_workers = max_workers
        if self._executor:
            self._executor.shutdown(wait=False)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def set_filters(self, include=None, exclude=None):
        self._include = include or []
        self._exclude = exclude or []

    def set_throttle(self, max_events_per_window, window_ms):
        self._throttle_limit = max_events_per_window
        self._throttle_window = window_ms / 1000.0

    def on_event(self, callback):
        self._callbacks.append(callback)

    def batch_dispatch(self, batch_interval_ms):
        self._batch_interval = batch_interval_ms / 1000.0
        if self._batch_thread and self._batch_thread.is_alive():
            return
        self._running = True
        self._batch_thread = threading.Thread(target=self._batch_loop, daemon=True)
        self._batch_thread.start()

    def configure_logging(self, level):
        lvl = getattr(logging, level.upper(), None)
        if lvl is None:
            raise ValueError(f"Invalid logging level: {level}")
        self._logger.setLevel(lvl)

    def set_polling_strategy(self, strategy):
        self._polling_strategy = strategy

    def apply_rate_limit(self, name, limit):
        self._rate_limits[name] = limit

    def run_single_scan(self, repo_path):
        for root, dirs, files in os.walk(repo_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                self._emit_event({
                    'type': 'created',
                    'path': fpath,
                    'timestamp': time.time()
                })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False
        if self._batch_thread:
            self._batch_event.set()
            self._batch_thread.join(timeout=1)
        if self._executor:
            self._executor.shutdown(wait=False)

    def _passes_filters(self, path):
        if self._include:
            matched = any(fnmatch(path, pat) for pat in self._include)
            if not matched:
                return False
        if self._exclude:
            if any(fnmatch(path, pat) for pat in self._exclude):
                return False
        return True

    def _throttle_check(self):
        if self._throttle_limit is None:
            return True
        now = time.time()
        window_start = now - self._throttle_window
        while self._throttle_times and self._throttle_times[0] < window_start:
            self._throttle_times.popleft()
        if len(self._throttle_times) < self._throttle_limit:
            self._throttle_times.append(now)
            return True
        return False

    def _emit_event(self, event):
        path = event.get('path', '')
        if not self._passes_filters(path):
            return
        if not self._throttle_check():
            return
        with self._batch_lock:
            if self._batch_interval:
                self._batch_queue.append(event)
            else:
                for cb in self._callbacks:
                    if self._executor:
                        self._executor.submit(cb, event)
                    else:
                        cb(event)

    def _batch_loop(self):
        while self._running:
            time.sleep(self._batch_interval)
            with self._batch_lock:
                if not self._batch_queue:
                    continue
                batch = list(self._batch_queue)
                self._batch_queue.clear()
            for cb in self._callbacks:
                if self._executor:
                    self._executor.submit(cb, batch)
                else:
                    cb(batch)
        # final flush
        with self._batch_lock:
            if self._batch_queue:
                batch = list(self._batch_queue)
                self._batch_queue.clear()
                for cb in self._callbacks:
                    if self._executor:
                        self._executor.submit(cb, batch)
                    else:
                        cb(batch)
