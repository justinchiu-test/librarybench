import os
import threading
import time
import logging
import asyncio
from collections import defaultdict

# Event class
class FileEvent:
    def __init__(self, type, src_path):
        self.type = type
        self.src_path = src_path

# Callbacks management
_callbacks = []
_callbacks_lock = threading.Lock()
_callback_id_counter = 0

# Rate limiting
_rate_limits = {}
_rate_limits_lock = threading.Lock()

# Retry policy
_retry_policy = {"max_retries": 0, "backoff": "none"}

# Change summary
_summary_counts = defaultdict(int)
_summary_lock = threading.Lock()
_summary_timer = None

# Async watcher(s)
_async_watchers = []  # list of (loop, queue)
_async_watchers_lock = threading.Lock()

# Watcher thread
_watcher_thread = None
_watcher_lock = threading.Lock()

# Scan interval for directory polling
_SCAN_INTERVAL = 0.1

def configure_logging(level):
    """
    Configure root logger to the specified level.
    """
    logging.basicConfig(level=level)
    logging.getLogger().setLevel(level)

def register_callback(event_type, handler, priority=0):
    """
    Register a callback for a given event type ('create', 'modify', 'delete').
    Returns a callback ID for later unregistration.
    """
    global _callback_id_counter
    with _callbacks_lock:
        cid = _callback_id_counter
        _callback_id_counter += 1
        _callbacks.append({
            "id": cid,
            "event_type": event_type,
            "handler": handler,
            "priority": priority
        })
    return cid

def unregister_callback(cid):
    """
    Unregister a previously registered callback by its ID.
    Returns True if removed, False if not found.
    """
    global _callbacks
    removed = False
    with _callbacks_lock:
        new_list = []
        for cb in _callbacks:
            if cb["id"] == cid:
                removed = True
            else:
                new_list.append(cb)
        _callbacks = new_list
    return removed

def configure_rate_limit(handler, max_events_per_sec):
    """
    Rate-limit a specific handler to at most max_events_per_sec events per second.
    """
    with _rate_limits_lock:
        _rate_limits[handler] = {
            "max": max_events_per_sec,
            "count": 0,
            "window_start": time.time()
        }

def set_retry_policy(max_retries, backoff_strategy):
    """
    Set global retry policy for handlers that raise exceptions.
    backoff_strategy: 'none' or 'exponential'
    """
    _retry_policy["max_retries"] = max_retries
    _retry_policy["backoff"] = backoff_strategy

def single_scan(path):
    """
    Perform a one-time recursive scan of the directory, returning all file paths.
    """
    result = []
    for root, dirs, files in os.walk(path):
        for f in files:
            result.append(os.path.join(root, f))
    result.sort()
    return result

def get_async_watcher():
    """
    Return an async iterator that yields FileEvent objects as they occur.
    Each watcher gets its own asyncio.Queue.
    """
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop
        loop = asyncio.get_event_loop()

    queue = asyncio.Queue()

    with _async_watchers_lock:
        _async_watchers.append((loop, queue))

    class AsyncWatcher:
        def __aiter__(self):
            return self

        async def __anext__(self):
            evt = await queue.get()
            return evt

    return AsyncWatcher()

def generate_change_summary(interval="every 30m"):
    """
    Periodically log a summary of change events seen ('create', 'modify', 'delete').
    Interval format: 'every 1s', 'every 5m', 'every 2h', etc.
    """
    global _summary_timer
    parts = interval.split()
    if len(parts) != 2 or parts[0] != "every":
        return
    spec = parts[1]
    try:
        num = int(spec[:-1])
        unit = spec[-1]
        if unit == "h":
            sec = num * 3600
        elif unit == "m":
            sec = num * 60
        else:
            sec = num
    except Exception:
        return

    def summarize():
        global _summary_timer
        with _summary_lock:
            counts = dict(_summary_counts)
            _summary_counts.clear()
        if counts:
            msg = ", ".join(f"{v} {k}" for k, v in counts.items())
            logging.info(f"Summary: {msg}")
        _summary_timer = threading.Timer(sec, summarize)
        _summary_timer.daemon = True
        _summary_timer.start()

    if _summary_timer is not None:
        _summary_timer.cancel()
    _summary_timer = threading.Timer(sec, summarize)
    _summary_timer.daemon = True
    _summary_timer.start()

def watch_directory(path):
    """
    Start watching a directory (and subdirectories) for file create/modify/delete events.
    Uses a polling approach in a background thread.
    """
    global _watcher_thread

    with _watcher_lock:
        if _watcher_thread is not None:
            return  # Already watching

        def _watcher_loop():
            # Build initial state: path -> mtime
            prev_state = {}
            for root, dirs, files in os.walk(path):
                for f in files:
                    p = os.path.join(root, f)
                    try:
                        prev_state[p] = os.path.getmtime(p)
                    except Exception:
                        prev_state[p] = None

            while True:
                current_state = {}
                for root, dirs, files in os.walk(path):
                    for f in files:
                        p = os.path.join(root, f)
                        try:
                            current_state[p] = os.path.getmtime(p)
                        except Exception:
                            current_state[p] = None

                prev_paths = set(prev_state.keys())
                curr_paths = set(current_state.keys())

                # Created files
                for p in curr_paths - prev_paths:
                    _dispatch_event(FileEvent("create", p))
                # Deleted files
                for p in prev_paths - curr_paths:
                    _dispatch_event(FileEvent("delete", p))
                # Modified files
                for p in prev_paths & curr_paths:
                    if prev_state.get(p) != current_state.get(p):
                        _dispatch_event(FileEvent("modify", p))

                prev_state = current_state
                time.sleep(_SCAN_INTERVAL)

        _watcher_thread = threading.Thread(target=_watcher_loop, daemon=True)
        _watcher_thread.start()

def _dispatch_event(event):
    """
    Internal: handle summary counting, async dispatch, and invoking callbacks.
    """
    # Summary counting
    with _summary_lock:
        _summary_counts[event.type] += 1

    # Async watcher enqueue
    with _async_watchers_lock:
        for loop, queue in list(_async_watchers):
            try:
                loop.call_soon_threadsafe(queue.put_nowait, event)
            except Exception:
                pass

    # Prepare callbacks snapshot
    with _callbacks_lock:
        cbs = list(_callbacks)
    cbs.sort(key=lambda cb: cb["priority"], reverse=True)

    for cb in cbs:
        if cb["event_type"] != event.type:
            continue
        handler = cb["handler"]

        # Rate limiting
        do_call = True
        with _rate_limits_lock:
            rl = _rate_limits.get(handler)
            if rl is not None:
                now = time.time()
                if now - rl["window_start"] >= 1.0:
                    rl["window_start"] = now
                    rl["count"] = 0
                if rl["count"] < rl["max"]:
                    rl["count"] += 1
                else:
                    do_call = False
        if not do_call:
            continue

        # Retry logic
        max_retries = _retry_policy.get("max_retries", 0)
        backoff = _retry_policy.get("backoff", "none")
        attempt = 0
        while True:
            try:
                handler(event)
                break
            except Exception:
                attempt += 1
                if attempt > max_retries:
                    break
                if backoff == "exponential":
                    time.sleep(2 ** (attempt - 1))
                # 'none' means immediate retry

# Expose dispatch_event publicly for tests
dispatch_event = _dispatch_event
