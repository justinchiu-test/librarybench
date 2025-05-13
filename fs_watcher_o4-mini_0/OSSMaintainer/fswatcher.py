import os
import time
import fnmatch
import threading
import logging
import uuid
import asyncio

# Event definition
class FileEvent:
    def __init__(self, event_type, src_path, dest_path=None, timestamp=None):
        self.type = event_type  # 'added', 'deleted', 'modified', 'moved'
        self.src_path = src_path
        self.dest_path = dest_path
        self.timestamp = timestamp or time.time()

# Global state
_callbacks = {}        # callback_id -> dict(pattern, func, priority)
_pollers = {}
_current_poller = 'simple'
_last_snapshots = {}
_summary_events = []
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)

# Rate limiting settings and state
_default_rate_limit_settings = {'max_events': 100, 'per_second': True}
_pending_rate_limit_settings = None
_rate_limit_settings = {}   # dirname -> settings dict
_rate_limit_state = {}      # dirname -> {'count': int, 'interval_start': float}

# Retry policy
_retry_policy = {
    'retries': 2,
    'backoff': 'constant'
}

# Core API
def register_callback(glob_pattern, callback, priority=0):
    cid = str(uuid.uuid4())
    _callbacks[cid] = {'pattern': glob_pattern, 'func': callback, 'priority': priority}
    return cid

def unregister_callback(callback_id):
    return _callbacks.pop(callback_id, None) is not None

def set_polling_strategy(name, PollerClass):
    _pollers[name] = PollerClass

def configure_logging(logger=None, level=logging.WARNING):
    global _logger
    if logger:
        _logger = logger
    _logger.setLevel(level)

def configure_rate_limit(max_events=100, per_second=True):
    """
    Configure rate limiting for the next new directory scan.
    Subsequent scan on that directory will use these settings.
    """
    global _pending_rate_limit_settings
    _pending_rate_limit_settings = {'max_events': max_events, 'per_second': per_second}

def set_retry_policy(retries=2, backoff='constant'):
    _retry_policy['retries'] = retries
    _retry_policy['backoff'] = backoff

def generate_change_summary(window='daily'):
    summary = {'added': 0, 'deleted': 0, 'modified': 0, 'moved': 0}
    for evt in _summary_events:
        summary[evt.type] = summary.get(evt.type, 0) + 1
    return summary

def single_scan(dirname):
    dirname = os.path.abspath(dirname)
    prev = _last_snapshots.get(dirname, {})
    curr = {}
    events = []
    # Walk directory
    for root, dirs, files in os.walk(dirname):
        for name in files:
            path = os.path.join(root, name)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            curr[path] = mtime
            if path not in prev:
                events.append(FileEvent('added', path))
            elif prev[path] != mtime:
                events.append(FileEvent('modified', path))
    for path in prev:
        if path not in curr:
            events.append(FileEvent('deleted', path))
    _last_snapshots[dirname] = curr

    # Rate limiting (per-directory)
    now = time.time()
    global _pending_rate_limit_settings
    # Initialize settings for this directory if needed
    if dirname not in _rate_limit_settings:
        # Use pending settings if provided, else default
        if _pending_rate_limit_settings is not None:
            settings = _pending_rate_limit_settings
            _pending_rate_limit_settings = None
        else:
            settings = _default_rate_limit_settings
        # Store settings and reset state for this directory
        _rate_limit_settings[dirname] = settings.copy()
        _rate_limit_state[dirname] = {'count': 0, 'interval_start': now}

    settings = _rate_limit_settings[dirname]
    state = _rate_limit_state.get(dirname, {'count': 0, 'interval_start': now})

    # If per-second window has elapsed, reset count
    if settings.get('per_second', False) and (now - state['interval_start'] >= 1):
        state['interval_start'] = now
        state['count'] = 0

    allowed = settings.get('max_events', 0) - state['count']
    if allowed <= 0:
        # update state and return no events
        _rate_limit_state[dirname] = state
        return []

    to_process = events[:allowed]
    state['count'] += len(to_process)
    _rate_limit_state[dirname] = state

    # Process events
    for evt in to_process:
        _summary_events.append(evt)
        _logger.debug(f"Event: {evt.type} {evt.src_path}")
        # Callbacks
        cbs = sorted(_callbacks.items(), key=lambda x: x[1]['priority'], reverse=True)
        for cid, info in cbs:
            pattern = info['pattern']
            func = info['func']
            if fnmatch.fnmatch(evt.src_path, pattern):
                _invoke_with_retry(func, evt)
    return to_process

def _invoke_with_retry(func, evt):
    attempts = 0
    delay = 0.1
    while True:
        try:
            func(evt)
            return
        except Exception as e:
            attempts += 1
            if attempts > _retry_policy['retries']:
                _logger.error(f"Callback failed after retries: {e}")
                return
            if _retry_policy.get('backoff') == 'exponential':
                time.sleep(delay)
                delay *= 2
            else:
                time.sleep(delay)

class SimplePoller(threading.Thread):
    def __init__(self, base_path, options=None):
        super().__init__()
        self.base_path = base_path
        self.options = options or {}
        self._stop = threading.Event()
        self.daemon = True

    def run(self):
        while not self._stop.is_set():
            single_scan(self.base_path)
            time.sleep(self.options.get('interval', 1))

    def stop(self):
        self._stop.set()

def watch_directory(base_path, options=None):
    if _current_poller not in _pollers:
        set_polling_strategy('simple', SimplePoller)
    PollerClass = _pollers.get(_current_poller)
    poller = PollerClass(base_path, options)
    poller.start()
    return poller

class AsyncWatcher:
    def __init__(self, base_path, loop=None, options=None):
        self.base_path = base_path
        self.loop = loop or asyncio.get_event_loop()
        self.options = options or {}

    def __aiter__(self):
        return self

    async def __anext__(self):
        events = await self.loop.run_in_executor(None, single_scan, self.base_path)
        if not events:
            await asyncio.sleep(self.options.get('interval', 1))
            raise StopAsyncIteration
        return events

def get_async_watcher(loop=None):
    return AsyncWatcher

# initialize default poller
set_polling_strategy('simple', SimplePoller)
