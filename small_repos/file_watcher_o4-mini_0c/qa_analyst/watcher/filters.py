import fnmatch

class FilterRules:
    def __init__(self, include=None, exclude=None, hide_dotfiles=True):
        self.include = include or []
        self.exclude = exclude or []
        self.hide_dotfiles = hide_dotfiles

    def add_include(self, pattern):
        self.include.append(pattern)

    def add_exclude(self, pattern):
        self.exclude.append(pattern)

    def remove_include(self, pattern):
        self.include = [p for p in self.include if p != pattern]

    def remove_exclude(self, pattern):
        self.exclude = [p for p in self.exclude if p != pattern]

    def match(self, path):
        if self.hide_dotfiles and any(part.startswith('.') for part in path.split('/')):
            return False
        matched = True
        if self.include:
            matched = any(fnmatch.fnmatch(path, pat) for pat in self.include)
        if self.exclude and matched:
            if any(fnmatch.fnmatch(path, pat) for pat in self.exclude):
                matched = False
        return matched
