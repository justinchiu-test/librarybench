import os
import time
import threading
import logging
import hashlib
import fnmatch
import builtins
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Expose logging in builtins so tests can refer to logging without importing it
builtins.logging = logging

class FileIntegrityMonitor:
    def __init__(self, root_path):
        self.root_path = root_path
        self.baseline = {}
        self.thread_pool_size = 4
        self.handler_timeout = 5  # seconds
        self.throttle_rate = None
        self.enable_move = False
        self.ignore_rules = []
        self.plugin_filters = []
        self.plugin_transforms = []
        self.sinks = []
        self.metrics_endpoints = []
        self.last_summary = ""
        self.logger = logging.getLogger("FileIntegrityMonitor")
        self.logger.setLevel(logging.INFO)

    def start_metrics_endpoint(self, callback):
        """Register a callback to receive metrics dict after each scan."""
        self.metrics_endpoints.append(callback)

    def set_thread_pool_size(self, size):
        self.thread_pool_size = size

    def set_handler_timeout(self, timeout):
        self.handler_timeout = timeout

    def set_throttle_rate(self, rate):
        self.throttle_rate = rate

    def configure_logging(self, level):
        self.logger.setLevel(level)

    def register_plugin(self, filter=None, transform=None, sink=None):
        if filter:
            self.plugin_filters.append(filter)
        if transform:
            self.plugin_transforms.append(transform)
        if sink:
            self.sinks.append(sink)

    def add_ignore_rule(self, pattern):
        self.ignore_rules.append(pattern)

    def enable_move_detection(self, enable=True):
        self.enable_move = enable

    def _is_ignored(self, path):
        name = os.path.basename(path)
        for pat in self.ignore_rules:
            if fnmatch.fnmatch(name, pat):
                return True
        for f in self.plugin_filters:
            try:
                if f(path):
                    return True
            except Exception:
                continue
        return False

    def _hash_file(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        for transform in self.plugin_transforms:
            try:
                data = transform(data)
            except Exception:
                continue
        return hashlib.sha256(data).hexdigest()

    def scan_once(self):
        start = time.time()
        current = {}
        files = []
        for dirpath, _, filenames in os.walk(self.root_path):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                if self._is_ignored(full):
                    continue
                files.append(full)
        # Hash files with thread pool
        hashes = {}
        with ThreadPoolExecutor(max_workers=self.thread_pool_size) as executor:
            future_map = {executor.submit(self._hash_file, p): p for p in files}
            for fut, path in future_map.items():
                try:
                    h = fut.result(timeout=self.handler_timeout)
                    hashes[path] = h
                except TimeoutError:
                    self.logger.warning(f"Timeout hashing file: {path}")
                except Exception as e:
                    self.logger.warning(f"Error hashing {path}: {e}")
        # Compare to baseline
        adds = set(hashes) - set(self.baseline)
        dels = set(self.baseline) - set(hashes)
        mods = set(p for p in hashes if p in self.baseline and hashes[p] != self.baseline[p])
        moves = set()
        if self.enable_move:
            # detect moves: same hash between adds and dels
            dels_hash_map = {self.baseline[p]: p for p in dels}
            to_remove_add = set()
            to_remove_del = set()
            for p in adds:
                h = hashes[p]
                if h in dels_hash_map:
                    moves.add((dels_hash_map[h], p))
                    to_remove_add.add(p)
                    to_remove_del.add(dels_hash_map[h])
            adds -= to_remove_add
            dels -= to_remove_del
        # Throttle events
        events = []
        for p in adds:
            events.append(('add', p))
        for p in dels:
            events.append(('delete', p))
        for p in mods:
            events.append(('modify', p))
        for src, dst in moves:
            events.append(('move', (src, dst)))
        if self.throttle_rate is not None and self.throttle_rate < len(events):
            events = events[:self.throttle_rate]
        # Dispatch sinks
        for evt, info in events:
            for sink in self.sinks:
                try:
                    sink(evt, info)
                except Exception:
                    continue
        # Update baseline
        self.baseline = hashes
        # Record metrics
        latency = time.time() - start
        metrics = {
            'anomaly_count': len(events),
            'latency': latency,
        }
        for cb in self.metrics_endpoints:
            try:
                cb(metrics)
            except Exception:
                continue
        # Summary
        self.last_summary = self.generate_change_summary(len(adds), len(dels), len(mods), len(moves))
        self.logger.info(f"Scan complete: {self.last_summary}")
        return {
            'added': adds,
            'deleted': dels,
            'modified': mods,
            'moved': moves,
            'metrics': metrics,
            'summary': self.last_summary,
        }

    def generate_change_summary(self, added, deleted, modified, moved):
        parts = []
        if added:
            parts.append(f"{added} files added")
        if deleted:
            parts.append(f"{deleted} files deleted")
        if modified:
            parts.append(f"{modified} files modified")
        if moved:
            parts.append(f"{moved} files moved")
        if not parts:
            return "No changes detected"
        return ", ".join(parts)
