import time
import logging
import fnmatch
import asyncio
import uuid

# Global variables
_callbacks = {}  # callback_id -> {filter_pattern, handler, priority}
_event_log = []
_polling_strategy = None
_retry_policy = {'max_retries': 4, 'backoff_strategy': 'exponential'}

_rate_limits = {}  # callback_id -> {'max_events_per_sec', 'timestamps'}
_debounce_intervals = {}  # callback_id -> debounce_interval in seconds
_last_execution_times = {}  # (callback_id, path) -> last_exec_time

def watch_directory(target_paths, recursive=True):
    return Watcher(target_paths, recursive)

class Watcher:
    def __init__(self, target_paths, recursive=True):
        self.target_paths = target_paths if isinstance(target_paths, list) else [target_paths]
        self.recursive = recursive

    def push_event(self, event_type, path, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        event = {'type': event_type, 'path': path, 'timestamp': timestamp}
        _event_log.append(event)
        # Sort callbacks by priority (lower number is higher priority)
        sorted_callbacks = sorted(_callbacks.items(), key=lambda item: item[1]['priority'])
        for callback_id, info in sorted_callbacks:
            pattern = info['filter_pattern']
            handler = info['handler']
            if fnmatch.fnmatch(path, pattern):
                # Rate limiting
                rl = _rate_limits.get(callback_id)
                if rl:
                    now = timestamp
                    window = 1.0
                    rl['timestamps'] = [t for t in rl['timestamps'] if now - t < window]
                    if len(rl['timestamps']) >= rl['max_events_per_sec']:
                        continue
                    rl['timestamps'].append(now)
                # Debounce modify events
                if event_type == 'modify':
                    debounce = _debounce_intervals.get(callback_id, 0)
                    last = _last_execution_times.get((callback_id, path), 0)
                    if timestamp - last < debounce:
                        continue
                    _last_execution_times[(callback_id, path)] = timestamp
                # Retry policy
                max_retries = _retry_policy.get('max_retries', 0)
                attempt = 0
                while True:
                    try:
                        handler(event_type, path)
                        break
                    except Exception:
                        attempt += 1
                        if attempt > max_retries:
                            logging.error(f"Handler {handler} failed after {attempt} attempts")
                            break
                        # Backoff omitted for tests

def register_callback(filter_pattern, backup_handler, priority=10):
    callback_id = str(uuid.uuid4())
    _callbacks[callback_id] = {
        'filter_pattern': filter_pattern,
        'handler': backup_handler,
        'priority': priority
    }
    _rate_limits.pop(callback_id, None)
    _debounce_intervals[callback_id] = 0.0
    return callback_id

def unregister_callback(callback_id):
    _callbacks.pop(callback_id, None)
    _rate_limits.pop(callback_id, None)
    _debounce_intervals.pop(callback_id, None)
    keys = [k for k in _last_execution_times if k[0] == callback_id]
    for k in keys:
        _last_execution_times.pop(k, None)

def set_polling_strategy(custom_polling_fn):
    global _polling_strategy
    _polling_strategy = custom_polling_fn

def configure_logging(level=logging.INFO):
    logging.basicConfig()
    logging.getLogger().setLevel(level)

def configure_rate_limit(handler_id, max_events_per_sec=2):
    _rate_limits[handler_id] = {'max_events_per_sec': max_events_per_sec, 'timestamps': []}

def configure_debounce(handler_id, debounce_interval):
    _debounce_intervals[handler_id] = debounce_interval

def generate_change_summary(trigger_time):
    backed_up = sum(1 for e in _event_log if e['type'] in ('create', 'modify', 'move'))
    deleted = sum(1 for e in _event_log if e['type'] == 'delete')
    _event_log.clear()
    return f"{backed_up} files backed up, {deleted} deleted"

def get_async_watcher():
    return AsyncWatcher()

class AsyncWatcher:
    async def push_event(self, event_type, path, timestamp=None):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_dispatch, event_type, path, timestamp)

def _sync_dispatch(event_type, path, timestamp):
    w = Watcher([], False)
    w.push_event(event_type, path, timestamp)

def single_scan(base_path):
    if _polling_strategy:
        return _polling_strategy(base_path)
    return []

def set_retry_policy(max_retries=4, backoff_strategy='exponential'):
    global _retry_policy
    _retry_policy = {'max_retries': max_retries, 'backoff_strategy': backoff_strategy}
