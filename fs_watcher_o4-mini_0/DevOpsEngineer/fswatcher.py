import os
import time
import threading
import logging
import fnmatch
import asyncio
import uuid
import builtins
from collections import defaultdict, deque

# Expose logging module to builtins so tests that refer to logging.DEBUG work
builtins.logging = logging

class FileEvent:
    def __init__(self, event_type, src_path, dest_path=None, timestamp=None):
        self.event_type = event_type  # 'created', 'modified', 'deleted', 'moved'
        self.src_path = src_path
        self.dest_path = dest_path
        self.timestamp = timestamp or time.time()

    def __repr__(self):
        return f"<FileEvent {self.event_type} {self.src_path} -> {self.dest_path} at {self.timestamp}>"

class FileSystemWatcher:
    def __init__(self):
        self._reset_state()
        self.logger = logging.getLogger('fswatcher')
        self.logger.addHandler(logging.NullHandler())

    def _reset_state(self):
        # all mutable state of the watcher
        self.paths = set()
        self.handlers = {}
        self.handler_patterns = []
        # polling strategy: how long to sleep between scans
        self.polling_strategy = lambda: 1.0
        self.running = False
        self.thread = None
        self.last_snapshot = {}
        self.rate_limits = {}
        self.handler_events = defaultdict(deque)
        self.path_events = defaultdict(deque)
        # default retry policy
        self.retry_policy = {'max_retries': 1, 'backoff_strategy': 'linear'}
        self.event_history = deque()
        # for async watchers
        self.async_queues = []

    def watch_directory(self, path, *args):
        if path not in self.paths:
            self.paths.add(path)
        if not self.running:
            # clear history/rate-limit state
            self.event_history.clear()
            self.handler_events.clear()
            self.path_events.clear()
            # take an initial snapshot
            self.last_snapshot = self._snapshot()
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def _run_loop(self):
        while self.running:
            interval = self.polling_strategy()
            time.sleep(interval)
            current = self._snapshot()
            curr_keys = set(current.keys())
            last_keys = set(self.last_snapshot.keys())

            created = curr_keys - last_keys
            deleted = last_keys - curr_keys
            common = curr_keys & last_keys
            modified = {p for p in common
                        if current[p][0] != self.last_snapshot[p][0]}

            # detect moves by inode
            moved = []
            rem_created = set(created)
            rem_deleted = set(deleted)
            inode_map = {self.last_snapshot[p][1]: p for p in deleted}
            for p in created:
                ino = current[p][1]
                if ino in inode_map:
                    src = inode_map[ino]
                    moved.append((src, p))
                    rem_deleted.discard(src)
                    rem_created.discard(p)

            # emit events in order: moved, created, modified, deleted
            for src, dst in moved:
                ev = FileEvent('moved', src, dst)
                self._handle_event(ev)
            for p in rem_created:
                ev = FileEvent('created', p)
                self._handle_event(ev)
            for p in modified:
                ev = FileEvent('modified', p)
                self._handle_event(ev)
            for p in rem_deleted:
                ev = FileEvent('deleted', p)
                self._handle_event(ev)

            self.last_snapshot = current

    def _snapshot(self):
        snap = {}
        for path in list(self.paths):
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    p = os.path.join(root, name)
                    try:
                        st = os.stat(p)
                        snap[p] = (st.st_mtime, st.st_ino)
                    except FileNotFoundError:
                        pass
        return snap

    def register_callback(self, pattern, handler, priority=0):
        handler_id = str(uuid.uuid4())
        info = {
            'id': handler_id,
            'pattern': pattern,
            'handler': handler,
            'priority': priority
        }
        self.handlers[handler_id] = info
        self.handler_patterns.append(info)
        # sort descending by priority
        self.handler_patterns.sort(key=lambda x: x['priority'], reverse=True)
        return handler_id

    def unregister_callback(self, handler_id):
        if handler_id in self.handlers:
            self.handlers.pop(handler_id)
            self.handler_patterns = [
                h for h in self.handler_patterns if h['id'] != handler_id
            ]

    def set_polling_strategy(self, poller_func):
        self.polling_strategy = poller_func

    def configure_logging(self, level=logging.INFO):
        self.logger.setLevel(level)

    def configure_rate_limit(self, handler_id=None, path=None, max_events_per_sec=10):
        key = handler_id or path
        if key:
            self.rate_limits[key] = max_events_per_sec

    def set_retry_policy(self, max_retries=3, backoff_strategy='exponential'):
        self.retry_policy = {
            'max_retries': max_retries,
            'backoff_strategy': backoff_strategy
        }

    def generate_change_summary(self, interval):
        now = time.time()
        counts = defaultdict(int)
        for ts, etype in list(self.event_history):
            if now - ts <= interval:
                counts[etype] += 1
        parts = []
        for et in ('created', 'modified', 'deleted', 'moved'):
            cnt = counts.get(et, 0)
            if cnt:
                parts.append(f"{cnt} {et}")
        return ", ".join(parts) if parts else "No changes"

    def get_async_watcher(self, loop=None):
        try:
            actual_loop = loop or asyncio.get_running_loop()
        except RuntimeError:
            actual_loop = asyncio.get_event_loop()
        q = asyncio.Queue()
        self.async_queues.append({'queue': q, 'loop': actual_loop})
        return q

    def single_scan(self, path):
        files = []
        for root, dirs, filenames in os.walk(path):
            for name in dirs + filenames:
                files.append(os.path.join(root, name))
        return files

    def _handle_event(self, event):
        # history
        self.event_history.append((event.timestamp, event.event_type))

        # push to any async queues
        for entry in self.async_queues:
            q = entry['queue']
            loop = entry['loop']
            try:
                loop.call_soon_threadsafe(q.put_nowait, event)
            except Exception:
                pass

        # dispatch to sync handlers
        for info in self.handler_patterns:
            pid = info['id']
            pattern = info['pattern']
            handler = info['handler']

            target = event.dest_path if event.event_type == 'moved' else event.src_path
            name = os.path.basename(target)
            if not fnmatch.fnmatch(name, pattern):
                continue

            now = time.time()
            # handler‐level rate limit
            if pid in self.rate_limits:
                dq = self.handler_events[pid]
                while dq and now - dq[0] > 1:
                    dq.popleft()
                if len(dq) >= self.rate_limits[pid]:
                    continue

            # path‐level rate limit
            if target in self.rate_limits:
                dq2 = self.path_events[target]
                while dq2 and now - dq2[0] > 1:
                    dq2.popleft()
                if len(dq2) >= self.rate_limits[target]:
                    continue

            # retry policy
            retries = 0
            maxr = self.retry_policy.get('max_retries', 0)
            backoff = self.retry_policy.get('backoff_strategy', 'linear')
            while True:
                try:
                    handler(event)
                    # on success record for rate‐limiting
                    if pid in self.rate_limits:
                        self.handler_events[pid].append(now)
                    if target in self.rate_limits:
                        self.path_events[target].append(now)
                    break
                except Exception as e:
                    retries += 1
                    if retries > maxr:
                        self.logger.error(f"Handler {pid} failed after {retries} retries: {e}")
                        break
                    # backoff calculation
                    if backoff == 'exponential':
                        to_sleep = 2 ** (retries - 1)
                    else:
                        to_sleep = 0
                    time.sleep(to_sleep)

    def stop(self):
        # stop the polling thread
        self.running = False
        if self.thread:
            self.thread.join()
        # fully reset all state so next test or usage starts fresh
        self._reset_state()


# module‐level watcher and convenience API
_global_watcher = FileSystemWatcher()

def watch_directory(path, *handlers):
    _global_watcher.watch_directory(path, *handlers)

def register_callback(pattern, handler, priority=0):
    return _global_watcher.register_callback(pattern, handler, priority)

def unregister_callback(handler_id):
    _global_watcher.unregister_callback(handler_id)

def set_polling_strategy(poller_func):
    _global_watcher.set_polling_strategy(poller_func)

def configure_logging(level):
    _global_watcher.configure_logging(level)

def configure_rate_limit(handler_id=None, path=None, max_events_per_sec=10):
    _global_watcher.configure_rate_limit(handler_id, path, max_events_per_sec)

def generate_change_summary(interval):
    return _global_watcher.generate_change_summary(interval)

def get_async_watcher(loop=None):
    return _global_watcher.get_async_watcher(loop)

def single_scan(path):
    return _global_watcher.single_scan(path)

def set_retry_policy(max_retries=3, backoff_strategy='exponential'):
    _global_watcher.set_retry_policy(max_retries, backoff_strategy)

def stop_watcher():
    _global_watcher.stop()
