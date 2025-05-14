import logging
import time
import threading
import asyncio
import fnmatch
import uuid

class Event:
    def __init__(self, event_type, path, timestamp=None, dest_path=None):
        self.event_type = event_type
        self.src_path = path
        self.dest_path = dest_path
        self.timestamp = timestamp if timestamp is not None else time.time()
    def __repr__(self):
        return f"<Event {self.event_type} {self.src_path} -> {self.dest_path} at {self.timestamp}>"

# Internal state
_callbacks = []
_callback_lock = threading.Lock()

_rate_limits = {}
_rate_limit_lock = threading.Lock()

_events = []

_retry_policy = {'max_retries': 0, 'backoff_strategy': None}

class DefaultPoller:
    def __init__(self):
        self._known = {}
    def poll(self, paths, recursive):
        # Default poller emits no events
        return []

_polling_strategy = DefaultPoller()

def watch_directory(paths, recursive=True):
    return Watcher(paths, recursive)

class Watcher:
    def __init__(self, paths, recursive):
        self.paths = paths if isinstance(paths, list) else [paths]
        self.recursive = recursive
        self._buffer = []
    def __iter__(self):
        return self
    def __next__(self):
        # Yield buffered events first; otherwise poll again
        while True:
            if self._buffer:
                return self._buffer.pop(0)
            events_dicts = _polling_strategy.poll(self.paths, self.recursive)
            if not events_dicts:
                time.sleep(0.1)
                continue
            # Buffer all new events
            for evt in events_dicts:
                event = Event(evt['event_type'],
                              evt['path'],
                              evt.get('timestamp'),
                              evt.get('dest_path'))
                _events.append(event)
                if _apply_rate_limit(event):
                    _invoke_callbacks(event)
                self._buffer.append(event)
            # Loop back to pop from buffer

def register_callback(pattern, handler, priority):
    with _callback_lock:
        handler_id = str(uuid.uuid4())
        _callbacks.append({'id': handler_id, 'pattern': pattern, 'handler': handler, 'priority': priority})
        _callbacks.sort(key=lambda x: x['priority'])
        return handler_id

def unregister_callback(handler_id):
    with _callback_lock:
        for cb in list(_callbacks):
            if cb['id'] == handler_id:
                _callbacks.remove(cb)
                return True
    return False

def set_polling_strategy(custom_poller):
    global _polling_strategy
    _polling_strategy = custom_poller

def configure_logging(logger, level=logging.INFO):
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(fmt)
        logger.addHandler(handler)

def configure_rate_limit(path='*', max_events_per_sec=1):
    with _rate_limit_lock:
        _rate_limits[path] = {'max_events_per_sec': max_events_per_sec, 'last_reset': time.time(), 'count': 0}

def _apply_rate_limit(event):
    with _rate_limit_lock:
        for pattern, rl in _rate_limits.items():
            if fnmatch.fnmatch(event.src_path, pattern):
                now = time.time()
                if now - rl['last_reset'] >= 1:
                    rl['last_reset'] = now
                    rl['count'] = 0
                rl['count'] += 1
                if rl['count'] > rl['max_events_per_sec']:
                    return False
    return True

def _invoke_callbacks(event):
    with _callback_lock:
        for cb in _callbacks:
            if fnmatch.fnmatch(event.src_path, cb['pattern']):
                try:
                    cb['handler'](event)
                except Exception:
                    pass

def generate_change_summary(period='hourly'):
    now = time.time()
    if period == 'hourly':
        duration = 3600
    elif period == 'minutely':
        duration = 60
    else:
        duration = 0
    csv_ingested = 0
    json_moved = 0
    for event in _events:
        if now - event.timestamp <= duration:
            if event.event_type == 'created' and event.src_path.lower().endswith('.csv'):
                csv_ingested += 1
            if event.event_type == 'moved' and event.src_path.lower().endswith('.json'):
                json_moved += 1
    return f"{csv_ingested} CSVs ingested, {json_moved} JSON logs moved"

class AsyncWatcher:
    def __init__(self, watcher):
        self._watcher = watcher
    async def next_event(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, next, self._watcher)

def get_async_watcher(paths, recursive=True):
    return AsyncWatcher(watch_directory(paths, recursive))

def single_scan(path):
    results = []
    # Use a fresh poller instance for one-time scan so as not to mutate global poller state
    poller = _polling_strategy
    try:
        temp_poller = type(poller)()
    except Exception:
        temp_poller = poller
    events_dicts = temp_poller.poll([path], False)
    for evt in events_dicts:
        event = Event(evt['event_type'],
                      evt['path'],
                      evt.get('timestamp'),
                      evt.get('dest_path'))
        _events.append(event)
        if _apply_rate_limit(event):
            _invoke_callbacks(event)
        results.append(event)
    return results

def set_retry_policy(max_retries=5, backoff_strategy='linear'):
    _retry_policy['max_retries'] = max_retries
    _retry_policy['backoff_strategy'] = backoff_strategy

def get_retry_policy():
    return _retry_policy.copy()
