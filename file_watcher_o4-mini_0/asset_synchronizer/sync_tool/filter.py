import fnmatch
import os

class FilterRules:
    def __init__(self, include=None, exclude=None, hidden=False, gitignore_path=None):
        self.include = include or []
        self.exclude = exclude or []
        self.hidden = hidden
        self.gitignore_patterns = []
        if gitignore_path and os.path.exists(gitignore_path):
            with open(gitignore_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.gitignore_patterns.append(line)

    def is_hidden(self, path):
        for part in path.split(os.sep):
            if part.startswith('.') and part not in ('.', '..'):
                return True
        return False

    def is_ignored_by_gitignore(self, path):
        for pat in self.gitignore_patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return True
        return False

    def is_allowed(self, path):
        if not self.hidden and self.is_hidden(path):
            return False
        if self.is_ignored_by_gitignore(path):
            return False
        if self.include and not any(fnmatch.fnmatch(path, pat) for pat in self.include):
            return False
        if any(fnmatch.fnmatch(path, pat) for pat in self.exclude):
            return False
        return True
