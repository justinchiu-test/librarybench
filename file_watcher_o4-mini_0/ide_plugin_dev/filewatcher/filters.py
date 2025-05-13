import fnmatch
import os

class FilterRules:
    def __init__(self):
        self.include_patterns = []
        self.exclude_patterns = []

    def add_include(self, pattern):
        self.include_patterns.append(pattern)

    def add_exclude(self, pattern):
        self.exclude_patterns.append(pattern)

    def clear(self):
        self.include_patterns.clear()
        self.exclude_patterns.clear()

    def match(self, path):
        # Exclude takes priority
        for pat in self.exclude_patterns:
            # exact match, wildcard, or prefix match (for directories)
            if fnmatch.fnmatch(path, pat) or path == pat or path.startswith(pat + os.sep):
                return False
        # If no include rules, accept everything not excluded
        if not self.include_patterns:
            return True
        # Otherwise, must match at least one include
        for pat in self.include_patterns:
            if fnmatch.fnmatch(path, pat) or path == pat or path.startswith(pat + os.sep):
                return True
        return False
