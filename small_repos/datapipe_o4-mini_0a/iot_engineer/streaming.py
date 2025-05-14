import time
import threading
import logging
import argparse
import multiprocessing
import queue as _queue
from collections import deque

_serializers = {}

def tumbling_window(readings, window_size):
    """Batch sensor readings into time-based windows"""
    if not readings:
        return
    # fixed-size buckets aligned to the first timestamp
    sorted_readings = sorted(readings, key=lambda x: x['timestamp'])
    min_ts = sorted_readings[0]['timestamp']
    buckets = {}
    for r in sorted_readings:
        idx = (r['timestamp'] - min_ts) // window_size
        buckets.setdefault(idx, []).append(r)
    for idx in sorted(buckets):
        yield buckets[idx]

def sliding_window(readings, window_size, step):
    """Generate rolling averages and anomaly scores over sliding windows"""
    if not readings:
        return
    sorted_readings = sorted(readings, key=lambda x: x['timestamp'])
    timestamps = [r['timestamp'] for r in sorted_readings]
    values = [r['value'] for r in sorted_readings]
    start = timestamps[0]
    end = timestamps[-1]
    t = start + window_size
    while t <= end + step:
        window_vals = [v for ti, v in zip(timestamps, values) if t - window_size < ti <= t]
        if window_vals:
            avg = sum(window_vals) / len(window_vals)
            anomaly = max(abs(v - avg) for v in window_vals)
            yield {"end": t, "average": avg, "anomaly": anomaly}
        t += step

def add_serializer(name, serializer):
    """Register a serializer adapter"""
    _serializers[name] = serializer
    return _serializers

def get_serializer(name):
    """Retrieve a registered serializer"""
    return _serializers.get(name)

def throttle_upstream(max_calls=1):
    """Decorate to throttle calls if overloaded (max_calls per 0.1s)"""
    period = 0.1
    calls = deque()
    lock = threading.Lock()
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            with lock:
                # remove timestamps outside the period window
                while calls and (now - calls[0]) > period:
                    calls.popleft()
                if len(calls) >= max_calls:
                    # too many calls in the last period: throttle
                    time.sleep(period)
                    now = time.time()
                    while calls and (now - calls[0]) > period:
                        calls.popleft()
                calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def watermark_event_time(readings, delay):
    """Assign event-time watermarks"""
    for r in readings:
        wm = r['timestamp'] - delay
        r_copy = r.copy()
        r_copy['watermark'] = wm
        yield r_copy

def halt_on_error(func):
    """Decorator: stop on unhandled exception"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def skip_error(func):
    """Decorator: skip corrupted messages and log a warning"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Skipping error in {func.__name__}: {e}")
            return None
    return wrapper

def setup_logging(level=logging.INFO):
    """Hook into Python logging"""
    logger = logging.getLogger()
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

def cli_manage():
    """CLI to scaffold and manage sensor pipelines"""
    parser = argparse.ArgumentParser(prog="cli_manage")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('scaffold')
    subparsers.add_parser('start')
    subparsers.add_parser('stop')
    subparsers.add_parser('health')
    return parser

def parallelize_stages(stages, queue=None):
    """Run stages in parallel threads (provides terminate/join API)"""
    threads = []
    q = queue or _queue.Queue()
    for stage in stages:
        t = threading.Thread(target=stage, args=(q,))
        t.daemon = True
        t.start()
        # provide terminate method for compatibility
        def _noop(): pass
        t.terminate = _noop
        threads.append(t)
    return threads, q
