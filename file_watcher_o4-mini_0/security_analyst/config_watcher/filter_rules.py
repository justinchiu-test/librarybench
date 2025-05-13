import threading
import fnmatch

class FilterRules:
    def __init__(self):
        self._include = []
        self._exclude = []
        self._lock = threading.Lock()

    def include(self, pattern):
        with self._lock:
            self._include.append(pattern)

    def exclude(self, pattern):
        with self._lock:
            self._exclude.append(pattern)

    def match(self, path):
        with self._lock:
            for pat in self._exclude:
                if fnmatch.fnmatch(path, pat):
                    return False
            if not self._include:
                return True
            for pat in self._include:
                if fnmatch.fnmatch(path, pat):
                    return True
            return False
