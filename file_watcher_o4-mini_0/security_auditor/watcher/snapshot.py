import hashlib
from pathlib import Path
from .filter import DynamicFilter

class Snapshot:
    def __init__(self, root, filter_rules=None):
        self.root = Path(root)
        self.filter = filter_rules or DynamicFilter()

    def load_gitignore(self):
        gitignore = self.root / ".gitignore"
        if gitignore.exists():
            for line in gitignore.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                self.filter.add_exclude(line)

    def take(self):
        self.load_gitignore()
        snap = {}
        for p in self.root.rglob('*'):
            if not p.is_file():
                continue
            # use path relative to root for filtering
            rel_path = p.relative_to(self.root)
            if not self.filter.match(rel_path):
                continue
            data = p.read_bytes()
            h = hashlib.sha256(data).hexdigest()
            snap[str(rel_path)] = h
        return snap

    @staticmethod
    def diff(old, new):
        added = [f for f in new if f not in old]
        removed = [f for f in old if f not in new]
        changed = [f for f in new if f in old and old[f] != new[f]]
        return {"added": added, "removed": removed, "changed": changed}
