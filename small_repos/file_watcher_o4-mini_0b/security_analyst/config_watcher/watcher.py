import asyncio
from .filter_rules import FilterRules
from .diffs import generate_diff

# Fallback stubs if watchdog is not installed
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    class FileSystemEventHandler:
        pass
    class Observer:
        def schedule(self, handler, path, recursive=True):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self):
            pass

class ConfigEventHandler(FileSystemEventHandler):
    def __init__(self, filter_rules, webhook_client, logger):
        self.filter = filter_rules
        self.webhook = webhook_client
        self.logger = logger
        self._snapshots = {}

    def _schedule_alert(self, action, path, detail=None):
        # Try to get the running loop; if none or not running, run synchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(self._alert(action, path, detail), loop)
        else:
            # run immediately in this thread
            asyncio.run(self._alert(action, path, detail))

    def on_created(self, event):
        if getattr(event, 'is_directory', False) or not self.filter.match(event.src_path):
            return
        self.logger.info(f"File created: {event.src_path}")
        self._schedule_alert('created', event.src_path)

    def on_deleted(self, event):
        if getattr(event, 'is_directory', False) or not self.filter.match(event.src_path):
            return
        self.logger.info(f"File deleted: {event.src_path}")
        self._schedule_alert('deleted', event.src_path)

    def on_modified(self, event):
        if getattr(event, 'is_directory', False) or not self.filter.match(event.src_path):
            return
        try:
            with open(event.src_path, 'r') as f:
                new = f.read()
        except Exception as e:
            self.logger.error(f"Read error: {e}")
            return
        old = self._snapshots.get(event.src_path, '')
        diff = generate_diff(old, new, fromfile=event.src_path, tofile=event.src_path)
        self._snapshots[event.src_path] = new
        self.logger.info(f"File modified: {event.src_path}")
        self._schedule_alert('modified', event.src_path, diff)

    def on_moved(self, event):
        if getattr(event, 'is_directory', False):
            return
        if not self.filter.match(event.dest_path):
            return
        self.logger.info(f"File moved from {event.src_path} to {event.dest_path}")
        detail = {'src': event.src_path, 'dest': event.dest_path}
        self._schedule_alert('moved', event.dest_path, detail)

    async def _alert(self, action, path, detail=None):
        payload = {'action': action, 'path': path, 'detail': detail}
        sent = await self.webhook.send(payload)
        if not sent:
            self.logger.error(f"Failed to send webhook for {path}")

class ConfigWatcher:
    def __init__(self, paths, webhook_client, logger, filter_rules=None):
        self.paths = paths
        self.webhook = webhook_client
        self.logger = logger
        self.filter = filter_rules or FilterRules()
        self._observer = Observer()

    async def start(self):
        handler = ConfigEventHandler(self.filter, self.webhook, self.logger)
        for p in self.paths:
            self._observer.schedule(handler, p, recursive=True)
        self._observer.start()
        self.logger.info("Watcher started")
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self._observer.stop()
            self._observer.join()
            await self.webhook.close()
            self.logger.info("Watcher stopped")
