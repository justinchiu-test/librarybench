import os
import asyncio
import fnmatch
import difflib
import logging
from typing import List, Callable, Dict, Optional, Any

class AsyncFileWatcher:
    def __init__(
        self,
        paths: List[str],
        includes: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
        recursive: bool = True,
        interval: float = 1.0,
        logger: Optional[logging.Logger] = None,
    ):
        self.paths = paths
        self.includes = includes or ["*"]
        self.excludes = excludes or []
        self.recursive = recursive
        self.interval = interval
        self.logger = logger or logging.getLogger("AsyncFileWatcher")
        self._handlers: List[Callable[[Dict[str, Any]], Any]] = []
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._snapshot: Dict[str, float] = {}
        self._content_cache: Dict[str, str] = {}

    def add_include(self, pattern: str):
        if pattern not in self.includes:
            self.includes.append(pattern)

    def remove_include(self, pattern: str):
        if pattern in self.includes:
            self.includes.remove(pattern)

    def add_exclude(self, pattern: str):
        if pattern not in self.excludes:
            self.excludes.append(pattern)

    def remove_exclude(self, pattern: str):
        if pattern in self.excludes:
            self.excludes.remove(pattern)

    def register_handler(self, handler: Callable[[Dict[str, Any]], Any]):
        self._handlers.append(handler)

    async def start(self):
        self.logger.info("Starting watcher")
        self._stop_event.clear()
        self._snapshot = {}
        for path in self.paths:
            self._scan_path(path, init=True)
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self.logger.info("Stopping watcher")
        self._stop_event.set()
        if self._task:
            await self._task
            self._task = None

    async def _run(self):
        while not self._stop_event.is_set():
            self._poll()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                continue

    def _scan_path(self, root: str, init: bool = False):
        if os.path.isfile(root):
            self._snapshot[root] = os.path.getmtime(root)
            if not init:
                self._content_cache[root] = self._read_file(root)
        else:
            for dirpath, dirnames, filenames in os.walk(root):
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    self._snapshot[fpath] = os.path.getmtime(fpath)
                    if not init:
                        self._content_cache[fpath] = self._read_file(fpath)
                if not self.recursive:
                    break

    def _poll(self):
        current: Dict[str, float] = {}
        for root in self.paths:
            if os.path.exists(root):
                if os.path.isfile(root):
                    current[root] = os.path.getmtime(root)
                else:
                    for dirpath, dirnames, filenames in os.walk(root):
                        for fname in filenames:
                            fpath = os.path.join(dirpath, fname)
                            current[fpath] = os.path.getmtime(fpath)
                        if not self.recursive:
                            break
        old_paths = set(self._snapshot.keys())
        new_paths = set(current.keys())
        created = new_paths - old_paths
        deleted = old_paths - new_paths
        common = new_paths & old_paths
        modified = set(p for p in common if current[p] != self._snapshot[p])
        # Update snapshot
        self._snapshot = current
        for path in created:
            if self._filter(path):
                event = {"type": "created", "path": path}
                asyncio.create_task(self._dispatch(event))
        for path in deleted:
            if self._filter(path):
                event = {"type": "deleted", "path": path}
                asyncio.create_task(self._dispatch(event))
                self._content_cache.pop(path, None)
        for path in modified:
            if self._filter(path):
                diff = self._compute_diff(path)
                event = {"type": "modified", "path": path, "diff": diff}
                asyncio.create_task(self._dispatch(event))

    def _filter(self, path: str) -> bool:
        basename = os.path.basename(path)
        matched_include = any(fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(basename, pat) for pat in self.includes)
        matched_exclude = any(fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(basename, pat) for pat in self.excludes)
        return matched_include and not matched_exclude

    def _read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().splitlines(keepends=True)
        except Exception:
            return []

    def _compute_diff(self, path: str) -> str:
        old = self._content_cache.get(path, [])
        new = self._read_file(path)
        self._content_cache[path] = new
        diff = difflib.unified_diff(old, new, fromfile="old", tofile="new", lineterm="")
        return "\n".join(diff)

    async def _dispatch(self, event: Dict[str, Any]):
        self.logger.debug(f"Dispatching event: {event}")
        for handler in self._handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self.logger.error(f"Error in handler: {e}")
