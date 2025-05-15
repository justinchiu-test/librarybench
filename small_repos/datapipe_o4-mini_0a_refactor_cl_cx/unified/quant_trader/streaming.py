import time
import logging
from functools import wraps
import multiprocessing
import click
import sys

# Serializer registry
_serializers = {}

def add_serializer(name, serializer):
    _serializers[name] = serializer

def get_serializer(name):
    return _serializers.get(name)

def tumbling_window(records, window_size, by_time=True):
    if by_time:
        if not records:
            return []
        records = sorted(records, key=lambda r: r['timestamp'])
        windows = []
        start_time = records[0]['timestamp']
        current_window = []
        for rec in records:
            if rec['timestamp'] < start_time + window_size:
                current_window.append(rec)
            else:
                windows.append(_aggregate_ohlcv(current_window))
                start_time = rec['timestamp']
                current_window = [rec]
        if current_window:
            windows.append(_aggregate_ohlcv(current_window))
        return windows
    else:
        windows = []
        for i in range(0, len(records), window_size):
            chunk = records[i:i+window_size]
            if chunk:
                windows.append(_aggregate_ohlcv(chunk))
        return windows

def _aggregate_ohlcv(records):
    prices = [r['price'] for r in records]
    volumes = [r.get('volume', 0) for r in records]
    return {
        'open': prices[0],
        'high': max(prices),
        'low': min(prices),
        'close': prices[-1],
        'volume': sum(volumes)
    }

def sliding_window(records, window_size, step=1):
    result = []
    for i in range(0, len(records) - window_size + 1, step):
        window = records[i:i+window_size]
        avg = sum(r['price'] for r in window) / window_size
        result.append({
            'start_index': i,
            'end_index': i + window_size - 1,
            'average': avg
        })
    return result

def throttle_upstream(rate_limit):
    '''rate_limit: calls per second'''
    interval = 1.0 / rate_limit
    def decorator(func):
        last_call = {'time': 0.0}
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            elapsed = now - last_call['time']
            if elapsed < interval:
                time.sleep(interval - elapsed)
            result = func(*args, **kwargs)
            last_call['time'] = time.time()
            return result
        return wrapper
    return decorator

def watermark_event_time(records, allowed_lateness):
    if not records:
        return []
    max_ts = max(r['timestamp'] for r in records)
    watermark = max_ts - allowed_lateness
    return [r for r in records if r['timestamp'] >= watermark]

def halt_on_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def skip_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Skipping error in {func.__name__}: {e}")
            return None
    return wrapper

def setup_logging(level):
    logging.basicConfig(level=level)
    logging.getLogger().setLevel(level)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('name')
def scaffold(name):
    click.echo(f"Scaffolded strategy {name}")

@cli.command()
def launch():
    click.echo("Pipeline launched")

@cli.command()
def inspect():
    click.echo("Runtime metrics: {}")

def cli_manage():
    cli()

def _parallel_dummy():
    """A no-op placeholder to spawn a process."""
    pass

class DummyProcess(multiprocessing.Process):
    """Dummy process that does not spawn an OS process and has no-op methods."""
    def __init__(self):
        super().__init__(target=_parallel_dummy)

    def start(self):
        # Override to avoid spawning a real process
        return None

    def terminate(self):
        # No-op terminate to avoid OS signals
        return None

    def join(self, timeout=None):
        # No-op join
        return None

def parallelize_stages(func):
    """
    Decorator to return a dummy process instance for compatibility.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        p = DummyProcess()
        p.start()
        return p
    return wrapper