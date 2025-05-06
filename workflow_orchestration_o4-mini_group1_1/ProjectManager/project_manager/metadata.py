import time
from typing import Dict, Any


class MetadataStorage:
    def __init__(self):
        # metadata per task name
        self._store: Dict[str, Dict[str, Any]] = {}

    def init_task(self, task_name: str):
        self._store[task_name] = {
            "start_time": None,
            "end_time": None,
            "duration": None,
            "state": None,
            "attempts": 0,
            "error": None,
        }

    def record_start(self, task_name: str):
        rec = self._store.setdefault(task_name, {})
        rec["start_time"] = time.time()
        rec["state"] = "running"

    def record_end(self, task_name: str, state: str, error: Exception = None):
        rec = self._store.setdefault(task_name, {})
        rec["end_time"] = time.time()
        start = rec.get("start_time") or rec["end_time"]
        rec["duration"] = rec["end_time"] - start
        rec["state"] = state
        rec["error"] = repr(error) if error else None

    def increment_attempt(self, task_name: str):
        rec = self._store.setdefault(task_name, {"attempts": 0})
        rec["attempts"] = rec.get("attempts", 0) + 1

    def get(self, task_name: str) -> Dict[str, Any]:
        return self._store.get(task_name, {})
