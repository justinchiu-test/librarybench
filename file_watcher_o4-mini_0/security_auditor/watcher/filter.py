import fnmatch
from pathlib import Path

class DynamicFilter:
    def __init__(self, include=None, exclude=None):
        self.include = list(include) if include else []
        self.exclude = list(exclude) if exclude else []

    def add_include(self, pattern):
        self.include.append(pattern)

    def add_exclude(self, pattern):
        self.exclude.append(pattern)

    def match(self, path):
        if isinstance(path, str):
            path = Path(path)
        p = path.as_posix()
        # hidden file filter
        if path.name.startswith('.'):
            return False
        # exclude patterns
        for pat in self.exclude:
            if fnmatch.fnmatch(p, pat):
                return False
        # include patterns if any
        if self.include:
            for pat in self.include:
                if fnmatch.fnmatch(p, pat):
                    return True
            return False
        return True
