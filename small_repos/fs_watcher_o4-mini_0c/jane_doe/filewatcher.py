import os
import time
import threading
import fnmatch
import logging
import hashlib
import json
import http.server
import socketserver
import concurrent.futures
from urllib.parse import urlparse
import signal

class FileWatcher:
    def __init__(self, paths=None):
        self.paths = paths or []
        self.ignore_rules = []
        self.plugins = []  # each plugin is dict with 'filter' and 'sink'
        self.thread_pool_size = 5
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_pool_size)
        self.handler_timeout = None
        self.throttle_rate = None  # events per second
        self.enable_move = False
        self.logger = logging.getLogger('FileWatcher')
        self._snapshot = {}
        self._last_events = []
        self._metrics = {
            'events_count': 0,
            'total_latency': 0.0,
            'events_processed': 0,
            'queue_size': 0
        }
        self.metrics_server = None
        self.metrics_thread = None
        self.metrics_port = None
        self._throttle_records = {}  # sink -> list of timestamps

    def add_path(self, path):
        self.paths.append(path)

    def add_ignore_rule(self, pattern):
        self.ignore_rules.append(pattern)

    def register_plugin(self, filter_fn, sink_fn):
        self.plugins.append({'filter': filter_fn, 'sink': sink_fn})
        self._throttle_records[sink_fn] = []

    def set_thread_pool_size(self, size):
        self.thread_pool_size = size
        self.executor.shutdown(wait=False)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_pool_size)

    def configure_logging(self, level):
        logging.basicConfig(level=level)
        self.logger.setLevel(level)

    def set_handler_timeout(self, timeout):
        self.handler_timeout = timeout

    def set_throttle_rate(self, rate):
        self.throttle_rate = rate

    def enable_move_detection(self):
        self.enable_move = True

    def start_metrics_endpoint(self, host='127.0.0.1', port=0):
        watcher = self
        class MetricsHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                data = {
                    'events_count': watcher._metrics['events_count'],
                    'avg_latency': (watcher._metrics['total_latency'] / watcher._metrics['events_processed']) if watcher._metrics['events_processed'] > 0 else 0.0,
                    'queue_size': watcher._metrics['queue_size']
                }
                resp = json.dumps(data).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
            def log_message(self, format, *args):
                return

        class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
            daemon_threads = True

        server = ThreadingHTTPServer((host, port), MetricsHandler)
        self.metrics_port = server.server_address[1]
        self.metrics_server = server
        def serve():
            server.serve_forever()
        t = threading.Thread(target=serve, daemon=True)
        t.start()
        self.metrics_thread = t

    def scan_once(self):
        current = {}
        for base in self.paths:
            for root, dirs, files in os.walk(base):
                for fname in files:
                    rel = os.path.join(root, fname)
                    ignore = False
                    for pat in self.ignore_rules:
                        if fnmatch.fnmatch(fname, pat):
                            ignore = True
                            break
                    if ignore:
                        continue
                    try:
                        stat = os.stat(rel)
                    except FileNotFoundError:
                        continue
                    mtime = stat.st_mtime
                    size = stat.st_size
                    h = hashlib.sha256()
                    try:
                        with open(rel, 'rb') as f:
                            h.update(f.read())
                        digest = h.hexdigest()
                    except Exception:
                        digest = f"{mtime}-{size}"
                    current[rel] = (mtime, size, digest)
        events = []
        old = self._snapshot
        added = set(current.keys()) - set(old.keys())
        removed = set(old.keys()) - set(current.keys())
        common = set(current.keys()) & set(old.keys())
        # detect created
        for p in added:
            events.append({'type': 'created', 'path': p, 'hash': current[p][2]})
        # detect deleted
        for p in removed:
            events.append({'type': 'deleted', 'path': p, 'hash': old[p][2]})
        # modified
        for p in common:
            if current[p][2] != old[p][2]:
                events.append({'type': 'modified', 'path': p, 'hash': current[p][2]})
        # move detection
        if self.enable_move:
            created = [e for e in events if e['type']=='created']
            deleted = [e for e in events if e['type']=='deleted']
            moved = []
            for d in deleted:
                for c in created:
                    if d['hash'] == c['hash']:
                        moved.append({'type':'moved', 'src_path': d['path'], 'dest_path': c['path'], 'hash': d['hash']})
            # remove matched created/deleted, add moved
            if moved:
                for m in moved:
                    events = [e for e in events if not ( (e.get('path')==m['src_path'] and e['type']=='deleted') or (e.get('path')==m['dest_path'] and e['type']=='created') )]
                events.extend(moved)
        self._snapshot = current
        self._last_events = events

        # prepare throttle records snapshot for this scan
        # throttle applies only when not using handler_timeout
        if self.throttle_rate and self.handler_timeout is None:
            now0 = time.time()
            prev_records = {}
            new_records = {}
            for plugin in self.plugins:
                sink_fn = plugin['sink']
                times = self._throttle_records.get(sink_fn, [])
                # prune older than 1s
                times = [t for t in times if now0 - t < 1.0]
                prev_records[sink_fn] = times
                new_records[sink_fn] = []
        else:
            prev_records = None
            new_records = None

        # dispatch events
        for ev in events:
            for plugin in self.plugins:
                filt = plugin['filter']
                sink = plugin['sink']
                try:
                    if not filt(ev):
                        continue
                except Exception:
                    continue
                # throttle per plugin (only for async branch)
                if self.throttle_rate and self.handler_timeout is None:
                    prev = prev_records.get(sink, [])
                    new = new_records.get(sink, [])
                    if len(prev) + len(new) >= self.throttle_rate:
                        continue
                    new.append(time.time())
                # handle with or without timeout
                if self.handler_timeout is not None:
                    # synchronous call with signal-based timeout
                    def _timeout_handler(signum, frame):
                        raise concurrent.futures.TimeoutError()
                    old_handler = signal.getsignal(signal.SIGALRM)
                    signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.setitimer(signal.ITIMER_REAL, self.handler_timeout)
                    start = time.time()
                    try:
                        sink(ev)
                        latency = time.time() - start
                        self._metrics['events_count'] += 1
                        self._metrics['total_latency'] += latency
                        self._metrics['events_processed'] += 1
                    except concurrent.futures.TimeoutError:
                        self.logger.error(f"Handler timeout for event {ev}")
                    except Exception as e:
                        self.logger.error(f"Handler error: {e}")
                    finally:
                        # disable timer and restore handler
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        signal.signal(signal.SIGALRM, old_handler)
                else:
                    start = time.time()
                    future = self.executor.submit(sink, ev)
                    try:
                        future.result()
                        latency = time.time() - start
                        self._metrics['events_count'] += 1
                        self._metrics['total_latency'] += latency
                        self._metrics['events_processed'] += 1
                    except concurrent.futures.TimeoutError:
                        future.cancel()
                        self.logger.error(f"Handler timeout for event {ev}")
                    except Exception as e:
                        self.logger.error(f"Handler error: {e}")

        # after dispatch, update global throttle records
        if self.throttle_rate and self.handler_timeout is None:
            for plugin in self.plugins:
                sink_fn = plugin['sink']
                prev = prev_records.get(sink_fn, [])
                new = new_records.get(sink_fn, [])
                self._throttle_records[sink_fn] = prev + new

        self._metrics['queue_size'] = self.executor._work_queue.qsize() if hasattr(self.executor, '_work_queue') else 0
        return events

    def generate_change_summary(self):
        counts = {'created':0, 'modified':0, 'deleted':0, 'moved':0}
        for ev in self._last_events:
            t = ev['type']
            if t in counts:
                counts[t] += 1
        parts = []
        if counts['created']:
            parts.append(f"{counts['created']} files created")
        if counts['modified']:
            parts.append(f"{counts['modified']} files modified")
        if counts['deleted']:
            parts.append(f"{counts['deleted']} files deleted")
        if counts['moved']:
            parts.append(f"{counts['moved']} files moved")
        if not parts:
            return "No changes"
        return ", ".join(parts)
