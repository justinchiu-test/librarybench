import time

class HistoryStore:
    def __init__(self):
        self._events = []

    def add(self, path, event_type):
        self._events.append({
            'path': path,
            'event_type': event_type,
            'timestamp': time.time()
        })

    def query(self, path=None, event_type=None):
        results = self._events
        if path is not None:
            results = [e for e in results if e['path'] == path]
        if event_type is not None:
            results = [e for e in results if e['event_type'] == event_type]
        return list(results)
