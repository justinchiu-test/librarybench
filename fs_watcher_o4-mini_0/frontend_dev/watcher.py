import time
import fnmatch
from threading import Lock

class Watcher:
    def __init__(self):
        self.metrics_started = False
        self.metrics_host = None
        self.metrics_port = None
        self.metrics_start_time = None
        self.reload_count = 0
        self.total_latency = 0.0

        self.filter_plugins = []
        self.transformer_plugins = []
        self.sink_plugins = []

        self.thread_pool_size = 1
        self.log_config = {}
        self.handler_timeout = None
        self.throttle_rate = None

        self.ignore_rules = []
        self.move_detection = False

        self.last_build_files = set()
        self._lock = Lock()

    def start_metrics_endpoint(self, host='localhost', port=8080):
        with self._lock:
            self.metrics_started = True
            self.metrics_host = host
            self.metrics_port = port
            self.metrics_start_time = time.time()
            self.reload_count = 0
            self.total_latency = 0.0

    def scan_once(self, files):
        start = time.time()
        filtered = []
        for f in files:
            # ignore rules
            if any(fnmatch.fnmatch(f, pat) for pat in self.ignore_rules):
                continue
            # filter plugins
            include = True
            for fn in self.filter_plugins:
                if not fn(f):
                    include = False
                    break
            if include:
                filtered.append(f)
        # apply transformers and sinks
        self.last_transformed = []
        self.last_sunk = []
        for f in filtered:
            for tf in self.transformer_plugins:
                res = tf(f)
                self.last_transformed.append((f, res))
            for sk in self.sink_plugins:
                res = sk(f)
                self.last_sunk.append((f, res))
        end = time.time()
        latency = end - start
        with self._lock:
            if self.metrics_started:
                self.reload_count += 1
                self.total_latency += latency
        return filtered

    def get_metrics(self):
        with self._lock:
            if not self.metrics_started or self.metrics_start_time is None:
                return None
            elapsed = time.time() - self.metrics_start_time
            rps = self.reload_count / elapsed if elapsed > 0 else 0.0
            avg = self.total_latency / self.reload_count if self.reload_count > 0 else 0.0
            return {
                'reloads_per_sec': rps,
                'avg_latency': avg
            }

    def register_plugin(self, plugin_type, callback):
        if plugin_type == 'filter':
            self.filter_plugins.append(callback)
        elif plugin_type == 'transformer':
            self.transformer_plugins.append(callback)
        elif plugin_type == 'sink':
            self.sink_plugins.append(callback)
        else:
            raise ValueError(f"Unknown plugin type: {plugin_type}")

    def set_thread_pool_size(self, size):
        if size < 1:
            raise ValueError("Thread pool size must be at least 1")
        self.thread_pool_size = size

    def configure_logging(self, level=None, fmt=None, destination=None):
        self.log_config = {
            'level': level,
            'format': fmt,
            'destination': destination
        }

    def set_handler_timeout(self, seconds):
        if seconds is not None and seconds < 0:
            raise ValueError("Timeout must be non-negative")
        self.handler_timeout = seconds

    def set_throttle_rate(self, rate):
        if rate is not None and rate < 0:
            raise ValueError("Throttle rate must be non-negative")
        self.throttle_rate = rate

    def generate_change_summary(self, current_files):
        current_set = set(current_files)
        changed = current_set.symmetric_difference(self.last_build_files)
        count = len(changed)
        self.last_build_files = current_set
        return f"Files changed since last build: {count}"

    def enable_move_detection(self):
        self.move_detection = True

    def add_ignore_rule(self, pattern):
        self.ignore_rules.append(pattern)
