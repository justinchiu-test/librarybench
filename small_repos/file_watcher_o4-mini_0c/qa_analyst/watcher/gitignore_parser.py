import os
import fnmatch

class GitignoreFilter:
    def __init__(self, gitignore_path):
        self.patterns = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    self.patterns.append(line)

    def ignores(self, path):
        for pat in self.patterns:
            if pat.endswith('/'):
                if path.startswith(pat.rstrip('/')):
                    return True
            if fnmatch.fnmatch(path, pat):
                return True
        return False
