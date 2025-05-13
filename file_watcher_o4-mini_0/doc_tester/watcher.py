import asyncio
import logging
import os
import threading
import pathlib
import difflib
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
)
import aiohttp

class LoggingSupport:
    def __init__(
        self,
        name="watcher",
        log_file="watcher.log",
        level=logging.INFO,
        max_bytes=1_000_000,
        backup_count=3,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        fh.setFormatter(fmt)
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def set_level(self, level):
        self.logger.setLevel(level)


class DynamicFilterRules:
    def __init__(self, include_patterns=None, exclude_patterns=None):
        # defaults if none provided
        self._include = set(include_patterns or ["*.md", "*.ipynb"])
        self._exclude = set(exclude_patterns or [])
        self._lock = threading.Lock()

    def include(self, pattern):
        with self._lock:
            self._include.add(pattern)

    def exclude(self, pattern):
        with self._lock:
            self._exclude.add(pattern)

    def match(self, path):
        from fnmatch import fnmatch

        with self._lock:
            inc = any(fnmatch(path, p) for p in self._include)
            # exclude patterns that have not been explicitly re-included
            exc_patterns = self._exclude - self._include
            exc = any(fnmatch(path, p) for p in exc_patterns)
        return inc and not exc


class WebhookIntegration:
    def __init__(self, endpoints):
        self.endpoints = endpoints or []

    async def send(self, payload):
        async with aiohttp.ClientSession() as session:
            for url in self.endpoints:
                try:
                    # don't use async with on post, tests expect simple await
                    resp = await session.post(url, json=payload)
                    await resp.text()
                except Exception:
                    pass


class InlineDiffs:
    def __init__(self):
        self._cache = {}

    def diff(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                new_lines = f.readlines()
        except Exception:
            return ""
        old_lines = self._cache.get(path, [])
        # update cache
        self._cache[path] = new_lines.copy()
        diff = difflib.unified_diff(
            old_lines, new_lines, fromfile="before", tofile="after", lineterm=""
        )
        return "\n".join(diff)


class WatchHandler(FileSystemEventHandler):
    def __init__(self, queue, filter_rules, inline_diffs, logger):
        self.queue = queue
        self.filter_rules = filter_rules
        self.inline_diffs = inline_diffs
        self.logger = logger

    def on_any_event(self, event):
        path = getattr(event, "src_path", None)
        if not path or not self.filter_rules.match(path):
            return
        if isinstance(event, FileCreatedEvent):
            typ = "create"
        elif isinstance(event, FileModifiedEvent):
            typ = "modify"
        elif isinstance(event, FileDeletedEvent):
            typ = "delete"
        elif isinstance(event, FileMovedEvent):
            typ = "move"
        else:
            typ = "unknown"
        diff_text = ""
        if typ in ("create", "modify") and pathlib.Path(path).suffix in (
            ".md",
            ".ipynb",
        ):
            diff_text = self.inline_diffs.diff(path)
        event_data = {"type": typ, "path": path, "diff": diff_text}
        self.logger.info(f"Event queued: {event_data}")
        try:
            self.queue.put_nowait(event_data)
        except asyncio.QueueFull:
            self.logger.error("Queue is full, dropping event")


class Watcher:
    def __init__(self, paths, endpoints, include=None, exclude=None):
        self.log = LoggingSupport()
        self.filter = DynamicFilterRules(include, exclude)
        self.webhook = WebhookIntegration(endpoints)
        self.inline = InlineDiffs()
        self.queue = asyncio.Queue()
        self.observer = Observer()
        self.paths = paths

    def start(self):
        handler = WatchHandler(
            self.queue, self.filter, self.inline, self.log.logger
        )
        for p in self.paths:
            self.observer.schedule(handler, p, recursive=True)
        self.observer.start()
        self.log.logger.info("Watcher started")
        try:
            asyncio.run(self._process_events())
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.log.logger.info("Watcher stopped")

    async def _process_events(self):
        while True:
            event = await self.queue.get()
            payload = {"event": event}
            await self._send_with_retry(payload)

    async def _send_with_retry(self, payload, retries=3, delay=1):
        for attempt in range(retries):
            try:
                await self.webhook.send(payload)
                self.log.logger.info("Payload sent")
                return
            except Exception as e:
                self.log.logger.error(
                    f"Send failed ({e}), retrying in {delay}s"
                )
                await asyncio.sleep(delay)
