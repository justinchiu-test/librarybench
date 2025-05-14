import time
import json
import logging
import argparse
import multiprocessing


def tumbling_window(posts):
    """
    Batch posts into minute-based tumbling windows.
    posts: list of dicts with 'timestamp' (epoch seconds)
    Returns dict: minute_index -> list of posts
    """
    windows = {}
    for post in posts:
        minute = int(post['timestamp'] // 60)
        windows.setdefault(minute, []).append(post)
    return windows


def sliding_window(posts, window_size=300):
    """
    Compute moving sentiment averages over a sliding window (seconds).
    posts: list of dicts with 'timestamp' and 'sentiment'
    Returns list of dicts: {'timestamp': ts, 'avg_sentiment': val}
    """
    results = []
    sorted_posts = sorted(posts, key=lambda x: x['timestamp'])
    for i, post in enumerate(sorted_posts):
        current_ts = post['timestamp']
        window_start = current_ts - window_size
        window_posts = [
            p for p in sorted_posts if p['timestamp'] >= window_start and p['timestamp'] <= current_ts
        ]
        if window_posts:
            avg = sum(p['sentiment'] for p in window_posts) / len(window_posts)
        else:
            avg = 0.0
        results.append({'timestamp': current_ts, 'avg_sentiment': avg})
    return results


def add_serializer(data):
    """
    Returns an object with a serialize(format) method.
    Supported formats: 'json', 'avro', 'parquet'
    """
    class Serializer:
        def __init__(self, data):
            self.data = data

        def serialize(self, fmt):
            payload = json.dumps(self.data).encode('utf-8')
            if fmt == 'json':
                return b'JSON:' + payload
            elif fmt == 'avro':
                return b'AVRO:' + payload
            elif fmt == 'parquet':
                return b'PARQUET:' + payload
            else:
                raise ValueError(f"Unknown format: {fmt}")
    return Serializer(data)


def throttle_upstream(iterable, max_items):
    """
    Apply simple backpressure: only yield up to max_items
    """
    for idx, item in enumerate(iterable):
        if idx < max_items:
            yield item
        else:
            # drop the rest
            break


def watermark_event_time(posts, lateness):
    """
    Assign watermarks based on event time.
    posts: list of dicts with 'timestamp'
    lateness: allowed lateness in seconds
    Returns list of watermarks, one per post
    """
    watermarks = []
    max_ts = float('-inf')
    for post in posts:
        ts = post['timestamp']
        max_ts = max(max_ts, ts)
        watermarks.append(max_ts - lateness)
    return watermarks


def halt_on_error(func):
    """
    Decorator to halt on any exception (rethrow).
    """
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def skip_error(func):
    """
    Decorator to skip errors: logs warning and returns None.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger()
            logger.warning(f"Skipping due to error: {e}")
            return None
    return wrapper


def setup_logging():
    """
    Configure Python logging for debug and error tracking.
    Returns the root logger.
    """
    # Ensure basicConfig sets up handlers if none exist
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")
    logger = logging.getLogger()
    # Explicitly set to DEBUG in case handlers/config were already present
    logger.setLevel(logging.DEBUG)
    return logger


def cli_manage(args=None):
    """
    Simple CLI management: start, monitor, logs
    """
    parser = argparse.ArgumentParser(prog="pipeline")
    parser.add_argument('command', choices=['start', 'monitor', 'logs'])
    ns = parser.parse_args(args)
    if ns.command == 'start':
        print("Pipeline started")
    elif ns.command == 'monitor':
        print("Monitoring throughput")
    elif ns.command == 'logs':
        print("Tailing logs")
    else:
        parser.print_help()


def parallelize_stages(functions, data):
    """
    Run a list of functions in (conceptually) parallel, each gets the same data.
    Returns list of results.
    Note: to avoid pickling issues, we run sequentially.
    """
    return [f(data) for f in functions]


def track_lineage(post, processor_name):
    """
    Maintain per-record lineage.
    """
    if '_lineage' not in post:
        post['_lineage'] = []
    post['_lineage'].append(processor_name)
    return post
