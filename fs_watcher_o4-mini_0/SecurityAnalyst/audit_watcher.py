import re
import threading
import time
import logging
import asyncio
import os
from collections import defaultdict, deque

# Global structures
_callbacks = {}
_handler_counter = 0
_events = []
_summary_counts = defaultdict(int)
_polling_strategy = None
_retry_policy = {'max_retries': 3, 'backoff_strategy': 'exponential'}
_security_logger = logging.getLogger('security')
_security_logger.addHandler(logging.NullHandler())

class RateLimiter:
    def __init__(self, max_events_per_minute):
        self.max_events = max_events_per_minute
        self.events = deque()

    def allow(self):
        now = time.time()
        window_start = now - 60
        while self.events and self.events[0] < window_start:
            self.events.popleft()
        if len(self.events) < self.max_events:
            self.events.append(now)
            return True
        return False

class Watcher:
    def __init__(self, sensitive_paths):
        self.sensitive_paths = sensitive_paths

    def simulate_event(self, event_type, path):
        timestamp = time.time()
        abs_path = os.path.abspath(path)
        event = {'type': event_type, 'path': abs_path, 'timestamp': timestamp}
        _events.append(event)
        _summary_counts[event_type] += 1
        # dispatch callbacks
        cbs = sorted(_callbacks.values(), key=lambda c: c['priority'])
        for cb in cbs:
            if re.search(cb['regex'], abs_path):
                limiter = cb.get('rate_limiter')
                if limiter and not limiter.allow():
                    continue
                tries = 0
                while True:
                    try:
                        cb['handler'](event)
                        break
                    except Exception:
                        tries += 1
                        if tries > _retry_policy['max_retries']:
                            _security_logger.error(f"Handler failed after {tries} retries")
                            break
                        # backoff
                        if _retry_policy['backoff_strategy'] == 'exponential':
                            time.sleep(2 ** (tries - 1))
                        else:
                            time.sleep(1)

def watch_directory(sensitive_paths):
    return Watcher(sensitive_paths)

def register_callback(path_regex, alert_handler, priority=100):
    global _handler_counter
    _handler_counter += 1
    cid = _handler_counter
    _callbacks[cid] = {
        'regex': path_regex,
        'handler': alert_handler,
        'priority': priority,
        'rate_limiter': None
    }
    return cid

def unregister_callback(handler_id):
    if handler_id in _callbacks:
        del _callbacks[handler_id]

def set_polling_strategy(audit_poller):
    global _polling_strategy
    _polling_strategy = audit_poller

def configure_logging(logger=None, level=logging.WARNING):
    global _security_logger
    if logger:
        _security_logger = logger
    _security_logger.setLevel(level)

def configure_rate_limit(alert_handler, max_events_per_minute=5):
    for cb in _callbacks.values():
        if cb['handler'] == alert_handler:
            cb['rate_limiter'] = RateLimiter(max_events_per_minute)

def generate_change_summary(period='daily'):
    parts = []
    for etype, count in _summary_counts.items():
        parts.append(f"{count} {etype}")
    return ", ".join(parts) + " detected."

class AsyncWatcher:
    def __init__(self, loop):
        self.loop = loop

    def dispatch(self, event):
        # Schedule all matching callbacks on the provided loop
        for cb in sorted(_callbacks.values(), key=lambda c: c['priority']):
            if re.search(cb['regex'], event['path']):
                # Use call_soon_threadsafe to queue the handler
                self.loop.call_soon_threadsafe(cb['handler'], event)
        # If the loop is not running, run a short sleep to allow scheduled callbacks to execute
        if not self.loop.is_running():
            # This will run once and process any queued call_soon_threadsafe callbacks
            self.loop.run_until_complete(asyncio.sleep(0))

def get_async_watcher(loop):
    return AsyncWatcher(loop)

def single_scan(config_dir):
    baseline = {}
    for root, dirs, files in os.walk(config_dir):
        for f in files:
            path = os.path.join(root, f)
            try:
                baseline[path] = os.path.getsize(path)
            except OSError:
                baseline[path] = None
    return baseline

def set_retry_policy(max_retries=3, backoff_strategy='exponential'):
    _retry_policy['max_retries'] = max_retries
    _retry_policy['backoff_strategy'] = backoff_strategy
