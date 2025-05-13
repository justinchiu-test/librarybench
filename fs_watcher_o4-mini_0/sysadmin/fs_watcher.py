import logging
import fnmatch
import time
import collections
import os
import threading

class Watcher:
    def __init__(self, config=None):
        self.config = config or {}
        self.pool_size = None
        self.include = []
        self.exclude = []
        self.events_per_sec = None
        self._throttle_timestamps = collections.deque()
        self.callback = None
        self.batch_interval_ms = None
        self._batch = []
        self._batch_lock = threading.Lock()
        self.rate_limits = {}  # key: {'limit', 'window_start', 'count'}
        self.polling_strategy = None
        self.logger = logging.getLogger(__name__)
        self.running = False

    def configure_thread_pool(self, pool_size):
        self.pool_size = pool_size

    def set_filters(self, include=None, exclude=None):
        self.include = include or []
        self.exclude = exclude or []

    def set_throttle(self, events_per_sec):
        self.events_per_sec = events_per_sec

    def on_event(self, callback):
        self.callback = callback

    def batch_dispatch(self, batch_interval_ms):
        self.batch_interval_ms = batch_interval_ms

    def configure_logging(self, level='WARNING'):
        self.logger.setLevel(getattr(logging, level))

    def set_polling_strategy(self, strategy):
        self.polling_strategy = strategy

    def apply_rate_limit(self, key, limit):
        self.rate_limits[key] = {
            'limit': limit,
            'window_start': time.time(),
            'count': 0
        }

    def run_single_scan(self, path):
        results = []
        for root, dirs, files in os.walk(path):
            for f in files:
                full = os.path.join(root, f)
                if self._filter_match(full):
                    results.append(full)
        return results

    def __enter__(self):
        self.running = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False

    def simulate_event(self, path, event_type):
        if not self.running:
            self.logger.warning("Watcher not running; event dropped")
            return
        if not self._filter_match(path):
            return
        now = time.time()
        # Throttle per sec
        if self.events_per_sec is not None:
            while self._throttle_timestamps and now - self._throttle_timestamps[0] >= 1:
                self._throttle_timestamps.popleft()
            if len(self._throttle_timestamps) >= self.events_per_sec:
                return
            self._throttle_timestamps.append(now)
        event = {'timestamp': now, 'path': path, 'type': event_type}
        if self.batch_interval_ms is None:
            self._dispatch_batch([event])
        else:
            with self._batch_lock:
                self._batch.append(event)

    def flush_batch(self):
        with self._batch_lock:
            batch = self._batch
            self._batch = []
        if batch:
            self._dispatch_batch(batch)

    def _dispatch_batch(self, events):
        # Apply rate limit if configured for 'siem_submitter'
        key = 'siem_submitter'
        if key in self.rate_limits:
            rl = self.rate_limits[key]
            now = time.time()
            # reset window if older than 1 sec
            if now - rl['window_start'] >= 1:
                rl['window_start'] = now
                rl['count'] = 0
            allowed = rl['limit'] - rl['count']
            if allowed <= 0:
                return
            to_send = events[:allowed]
            rl['count'] += len(to_send)
        else:
            to_send = events
        if self.callback:
            try:
                self.callback(to_send)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def _filter_match(self, path):
        # Exclude patterns first
        for pat in self.exclude:
            if fnmatch.fnmatch(path, pat):
                return False
        # Include patterns
        if not self.include:
            return True
        for pat in self.include:
            if fnmatch.fnmatch(path, pat):
                return True
        return False
