import logging

class FileWatcher:
    def __init__(self):
        self.metrics_started = False
        self.metrics_port = None
        self.plugins = {}
        self.thread_pool_size = 1
        self.handler_timeout = None
        self.throttle_rate = None
        self.ignore_rules = []
        self.move_detection = False

    def start_metrics_endpoint(self, port=8000):
        self.metrics_port = port
        self.metrics_started = True

    def scan_once(self, directory):
        # Stub implementation for directory scan
        return []

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin

    def set_thread_pool_size(self, size):
        self.thread_pool_size = size

    def configure_logging(self, level=logging.INFO, fmt=None):
        # Ensure the root logger level is always set, even if handlers already exist
        if fmt is not None:
            logging.basicConfig(level=level, format=fmt, force=True)
        else:
            logging.basicConfig(level=level, force=True)

    def set_handler_timeout(self, timeout_seconds):
        self.handler_timeout = timeout_seconds

    def set_throttle_rate(self, rate):
        self.throttle_rate = rate

    def generate_change_summary(self, ingested, failed):
        return f"{ingested} files ingested, {failed} failed validation"

    def enable_move_detection(self):
        self.move_detection = True

    def add_ignore_rule(self, pattern):
        self.ignore_rules.append(pattern)

# Singleton instance and module-level functions
watcher = FileWatcher()

def start_metrics_endpoint(port=8000):
    watcher.start_metrics_endpoint(port)

def scan_once(directory):
    return watcher.scan_once(directory)

def register_plugin(name, plugin):
    watcher.register_plugin(name, plugin)

def set_thread_pool_size(size):
    watcher.set_thread_pool_size(size)

def configure_logging(level=logging.INFO, fmt=None):
    watcher.configure_logging(level, fmt)

def set_handler_timeout(timeout_seconds):
    watcher.set_handler_timeout(timeout_seconds)

def set_throttle_rate(rate):
    watcher.set_throttle_rate(rate)

def generate_change_summary(ingested, failed):
    return watcher.generate_change_summary(ingested, failed)

def enable_move_detection():
    watcher.enable_move_detection()

def add_ignore_rule(pattern):
    watcher.add_ignore_rule(pattern)
