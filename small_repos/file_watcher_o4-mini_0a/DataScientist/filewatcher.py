import asyncio
import os
import time
from utils import retry
from event_history_store import EventHistoryStore
from cicd import CiCdTrigger

class FileWatcher:
    def __init__(
        self,
        directory,
        follow_symlinks=False,
        dry_run=False,
        hidden_filter=True,
        throttle_interval=1.0,
        cicd_triggers=None,
        history_store=None
    ):
        self.directory = directory
        self.follow_symlinks = follow_symlinks
        self.dry_run = dry_run
        self.hidden_filter = hidden_filter
        self.throttle_interval = throttle_interval
        self.history_store = history_store or EventHistoryStore()
        self.handlers = {'created': [], 'modified': []}
        self.cicd_triggers = cicd_triggers or []
        self._seen = {}
        self._queue = asyncio.Queue()
        self._stop_event = asyncio.Event()

    def register_handler(self, event_type, handler):
        if event_type not in self.handlers:
            raise ValueError("Unknown event type")
        self.handlers[event_type].append(handler)

    def start_cli(self):
        asyncio.create_task(self._tail())

    async def _tail(self):
        while not self._stop_event.is_set():
            path, etype, ts = await self._queue.get()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}] {etype}: {path}")

    async def scan(self):
        for root, dirs, files in os.walk(self.directory, followlinks=self.follow_symlinks):
            for name in files:
                if self.hidden_filter and name.startswith(('.', '~')):
                    continue
                path = os.path.join(root, name)
                try:
                    stat = os.stat(path)
                except Exception:
                    continue
                mtime = stat.st_mtime
                old = self._seen.get(path)
                if old is None:
                    yield path, 'created', mtime
                elif mtime > old:
                    yield path, 'modified', mtime
                self._seen[path] = mtime

    @retry(Exception, tries=3, delay=1)
    async def _handle_event(self, path, etype, ts):
        self.history_store.log_event(path, etype, ts)
        await self._queue.put((path, etype, ts))
        for handler in self.handlers.get(etype, []):
            if not self.dry_run:
                await handler(path)
        for trigger in self.cicd_triggers:
            if not self.dry_run:
                await trigger.trigger(path, etype)

    async def run(self):
        while not self._stop_event.is_set():
            start = time.time()
            async for path, etype, ts in self.scan():
                await self._handle_event(path, etype, ts)
            dur = time.time() - start
            sleep = max(0, self.throttle_interval - dur)
            await asyncio.sleep(sleep)

    def stop(self):
        self._stop_event.set()
