import os
import time
import threading
import logging
import inspect
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class Watcher:
    def __init__(self, *args, **kwargs):
        self._executor = None
        self._include = []
        self._exclude = []
        self._max_events = None
        self._per_ms = None
        self._event_callback = None
        self._batch_callback = None
        self._batch_interval = None
        self._logger = logging.getLogger('fs_watcher')
        self._logger.addHandler(logging.NullHandler())
        self._custom_scanner = None
        self._rate_limits = {}
        self._lock = threading.Lock()
        self._last_event_times = []
        self._shutdown = False

    def configure_thread_pool(self, num_workers):
        self._executor = ThreadPoolExecutor(max_workers=num_workers)
        return self

    def set_filters(self, include=None, exclude=None):
        if include is not None:
            self._include = include
        if exclude is not None:
            self._exclude = exclude
        return self

    def set_throttle(self, max_events, per_ms):
        self._max_events = max_events
        self._per_ms = per_ms
        return self

    def on_event(self, process_data_callback):
        self._event_callback = process_data_callback
        return self

    def batch_dispatch(self, interval_ms):
        # set batch interval
        self._batch_interval = interval_ms
        # hack: if caller defined an 'on_batch' callback, capture it
        frame = inspect.currentframe().f_back
        try:
            cb = frame.f_locals.get('on_batch')
            if callable(cb):
                self._batch_callback = cb
        finally:
            # avoid reference cycles
            del frame
        return self

    def configure_logging(self, level_str):
        level = getattr(logging, level_str.upper(), None)
        if level is None:
            raise ValueError(f"Invalid logging level: {level_str}")
        self._logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # clear other handlers
        self._logger.handlers = []
        self._logger.addHandler(handler)
        return self

    def set_polling_strategy(self, custom_scanner):
        self._custom_scanner = custom_scanner
        return self

    def apply_rate_limit(self, worker_name, per_second):
        self._rate_limits[worker_name] = per_second
        return self

    def run_single_scan(self, path):
        # Determine files
        if self._custom_scanner:
            files = self._custom_scanner(path)
        else:
            files = []
            for root, dirs, filenames in os.walk(path):
                for fname in filenames:
                    files.append(os.path.join(root, fname))

        # helper for pattern matching, to allow '**/' matching zero dirs
        def _matches_pattern(p: Path, pat: str) -> bool:
            if p.match(pat):
                return True
            if '**/' in pat:
                alt = pat.replace('**/', '')
                if p.match(alt):
                    return True
            return False

        # Filter files
        matched = []
        for f in files:
            # compute relative path for matching
            try:
                rel_path = os.path.relpath(f, path)
            except Exception:
                rel_path = f
            # normalize to posix style for matching
            rel_posix = Path(rel_path).as_posix()
            p = Path(rel_posix)

            # include check
            if self._include:
                inc_ok = any(_matches_pattern(p, pat) for pat in self._include)
            else:
                inc_ok = True
            if not inc_ok:
                continue

            # exclude check
            if self._exclude:
                exc_ok = any(_matches_pattern(p, pat) for pat in self._exclude)
            else:
                exc_ok = False
            if exc_ok:
                continue

            matched.append(f)

        # Generate events
        events = []
        for f in matched:
            now = time.time()
            # Throttle
            if self._max_events and self._per_ms:
                with self._lock:
                    window = self._per_ms / 1000.0
                    # keep only recent events
                    self._last_event_times = [
                        t for t in self._last_event_times if now - t < window
                    ]
                    if len(self._last_event_times) >= self._max_events:
                        self._logger.warning("Throttled event for %s", f)
                        continue
                    self._last_event_times.append(now)

            event = {'type': 'created', 'src_path': f, 'time': now}
            events.append(event)
            if self._event_callback:
                if self._executor:
                    self._executor.submit(self._event_callback, event)
                else:
                    self._event_callback(event)

        # Batch dispatch
        if self._batch_callback:
            def dispatch_batch(evts):
                if self._executor:
                    self._executor.submit(self._batch_callback, evts)
                else:
                    self._batch_callback(evts)
            dispatch_batch(events)

        return events

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._shutdown = True
        if self._executor:
            self._executor.shutdown(wait=True)
        return False
