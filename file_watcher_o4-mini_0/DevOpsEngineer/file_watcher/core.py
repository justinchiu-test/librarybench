import time
import re
import asyncio
import functools

class Event:
    def __init__(self, path, type, timestamp=None):
        self.path = path
        self.type = type
        self.timestamp = timestamp or time.time()
    def __repr__(self):
        return f"<Event type={self.type} path={self.path} ts={self.timestamp}>"

class EventHistoryStore:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.events = []
    def add(self, event):
        while len(self.events) >= self.max_size:
            self.events.pop(0)
        self.events.append(event)
    def get_events(self, filter_fn=None):
        if filter_fn is None:
            return list(self.events)
        return [e for e in self.events if filter_fn(e)]

class SymlinkConfig:
    FOLLOW = 'follow'
    IGNORE = 'ignore'
    SPECIAL = 'special'

class HiddenFileFilter:
    def __init__(self, ignore_hidden=True):
        self.ignore_hidden = ignore_hidden
    def allow(self, path):
        name = path.split('/')[-1]
        if self.ignore_hidden and name.startswith('.'):
            return False
        return True

class ErrorHandler:
    def __init__(self, retries=3, backoff_factor=0.1):
        self.retries = retries
        self.backoff_factor = backoff_factor
    def retry(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = self.backoff_factor
            for attempt in range(self.retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt < self.retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
        return wrapper

class Plugin:
    def __init__(self):
        self.triggered = []
    def fire(self, event, dry_run=False):
        entry = event if not dry_run else ('dry', event)
        self.triggered.append(entry)

class JenkinsPlugin(Plugin):
    pass

class GitHubActionsPlugin(Plugin):
    pass

class GitLabCIPlugin(Plugin):
    pass

class HandlerRegistration:
    def __init__(self):
        self.handlers = []
    def register(self, event_type, pattern, callback):
        regex = re.compile(pattern)
        self.handlers.append((event_type, regex, callback))
    def dispatch(self, event):
        for et, regex, callback in self.handlers:
            if (et == '*' or et == event.type) and regex.search(event.path):
                callback(event)

class Throttler:
    def __init__(self, rate=0):
        self.rate = rate  # events per second
        self.timestamps = []
    def allow(self, event):
        if self.rate <= 0:
            return True
        now = time.time()
        window_start = now - 1
        self.timestamps = [t for t in self.timestamps if t >= window_start]
        if len(self.timestamps) < self.rate:
            self.timestamps.append(now)
            return True
        return False

class FileWatcher:
    def __init__(
        self,
        dry_run=False,
        symlink=SymlinkConfig.FOLLOW,
        ignore_hidden=False,
        throttle_rate=0,
        history_max_size=1000,
        retries=3,
        backoff_factor=0.1,
    ):
        self.dry_run_mode = type('DR', (), {'dry_run': dry_run})
        self.symlink_config = symlink
        self.hidden_filter = HiddenFileFilter(ignore_hidden)
        self.throttler = Throttler(throttle_rate)
        self.store = EventHistoryStore(history_max_size)
        self.error_handler = ErrorHandler(retries, backoff_factor)
        self.handler_reg = HandlerRegistration()
        self.plugins = []
    def register_handler(self, event_type, pattern, callback):
        self.handler_reg.register(event_type, pattern, callback)
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    def trigger_event(self, path, event_type):
        event = Event(path, event_type, time.time())
        # filter hidden files
        if not self.hidden_filter.allow(path):
            return None
        # symlink handling: simplistic
        if self.symlink_config == SymlinkConfig.IGNORE and 'symlink' in path:
            return None
        # throttling
        if not self.throttler.allow(event):
            return None
        # store history
        self.store.add(event)
        # dispatch handlers
        self.handler_reg.dispatch(event)
        # fire plugins
        for p in self.plugins:
            p.fire(event, self.dry_run_mode.dry_run)
        return event
    async def trigger_event_async(self, path, event_type):
        return self.trigger_event(path, event_type)
