import threading
import multiprocessing
import time
import logging
import argparse
import sys
from queue import Queue

serializers = {}
lineage_store = {}

def tumbling_window(transactions, window_size):
    if not transactions or window_size <= 0:
        return []
    sorted_tx = sorted(transactions, key=lambda x: x['timestamp'])
    windows = []
    start = sorted_tx[0]['timestamp']
    end = start + window_size
    current = []
    for tx in sorted_tx:
        ts = tx['timestamp']
        if ts < end:
            current.append(tx)
        else:
            windows.append(current)
            current = [tx]
            start = end
            end = start + window_size
    if current:
        windows.append(current)
    return windows

def sliding_window(transactions, window_size, slide=None):
    if not transactions or window_size <= 0:
        return []
    if slide is None:
        slide = window_size
    sorted_tx = sorted(transactions, key=lambda x: x['timestamp'])
    result = []
    min_ts = sorted_tx[0]['timestamp']
    max_ts = sorted_tx[-1]['timestamp']
    start = min_ts
    while start <= max_ts:
        end = start + window_size
        window = [tx for tx in sorted_tx if start <= tx['timestamp'] < end]
        result.append(window)
        start += slide
    return result

def add_serializer(name, serializer_fn):
    serializers[name] = serializer_fn

def throttle_upstream(max_queue_size):
    def decorator(fn):
        def wrapper(q, *args, **kwargs):
            try:
                size = q.qsize()
                if size > max_queue_size:
                    time.sleep(0.01)
            except Exception:
                pass
            return fn(q, *args, **kwargs)
        return wrapper
    return decorator

def watermark_event_time(events, allowed_lateness):
    if not events or allowed_lateness < 0:
        return []
    max_ts = max(e['timestamp'] for e in events)
    watermark = max_ts - allowed_lateness
    result = []
    for e in events:
        tagged = dict(e)
        tagged['watermark'] = watermark
        tagged['is_late'] = e['timestamp'] < watermark
        result.append(tagged)
    return result

def halt_on_error(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)  # exceptions propagate
    return wrapper

def skip_error(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Skipping error in {fn.__name__}: {e}")
            return None
    return wrapper

def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def cli_manage():
    parser = argparse.ArgumentParser(prog="compliance_cli")
    sub = parser.add_subparsers(dest='command')
    audit = sub.add_parser('audit')
    audit.add_argument('--window_size', type=int, default=60)
    show = sub.add_parser('show-logs')
    deploy = sub.add_parser('deploy-rules')
    deploy.add_argument('--rule-file', type=str, required=True)
    args = parser.parse_args()
    if args.command == 'audit':
        print(f"Running audit with window size {args.window_size}")
    elif args.command == 'show-logs':
        print("Displaying logs")
    elif args.command == 'deploy-rules':
        print(f"Deploying rules from {args.rule_file}")
    else:
        parser.print_help()
    return 0

def parallelize_stages(stages, data):
    results = {}
    threads = []
    def run_stage(name, fn, input_data):
        results[name] = fn(input_data)
    for name, fn in stages.items():
        t = threading.Thread(target=run_stage, args=(name, fn, data))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results

def track_lineage(fn):
    def wrapper(record, *args, **kwargs):
        rec_id = record.get('id')
        if rec_id is None:
            return fn(record, *args, **kwargs)
        lineage = lineage_store.setdefault(rec_id, [])
        lineage.append(fn.__name__)
        return fn(record, *args, **kwargs)
    return wrapper
