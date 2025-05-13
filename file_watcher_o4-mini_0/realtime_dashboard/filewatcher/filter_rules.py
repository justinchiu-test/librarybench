import fnmatch
import os

class DynamicFilterRules:
    def __init__(self):
        self.include_patterns = []
        self.exclude_patterns = []

    def add_include(self, pattern: str):
        self.include_patterns.append(pattern)

    def add_exclude(self, pattern: str):
        self.exclude_patterns.append(pattern)

    def match(self, path: str) -> bool:
        # Match patterns against the basename, not the full path
        name = os.path.basename(path)
        # If we have include patterns, require at least one match.
        if self.include_patterns:
            matched_include = any(fnmatch.fnmatch(name, pat) for pat in self.include_patterns)
        else:
            matched_include = True
        # Exclude wins.
        matched_exclude = any(fnmatch.fnmatch(name, pat) for pat in self.exclude_patterns)
        return matched_include and not matched_exclude
