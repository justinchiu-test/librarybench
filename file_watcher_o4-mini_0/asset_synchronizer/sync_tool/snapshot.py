import os
import hashlib

class Snapshot:
    def __init__(self, root, file_hash=False, filter_rules=None):
        self.root = root
        self.file_hash = file_hash
        self.filter_rules = filter_rules
        self.files = {}
        self._take_snapshot()

    def _take_snapshot(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            for fname in filenames:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), self.root)
                if self.filter_rules and not self.filter_rules.is_allowed(rel_path):
                    continue
                full_path = os.path.join(dirpath, fname)
                stat = os.stat(full_path)
                entry = {'mtime': stat.st_mtime}
                if self.file_hash:
                    entry['hash'] = self._hash_file(full_path)
                self.files[rel_path] = entry

    def _hash_file(self, path, block_size=65536):
        sha1 = hashlib.sha1()
        with open(path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def diff(self, other):
        added = []
        removed = []
        modified = []
        for path, info in self.files.items():
            if path not in other.files:
                added.append(path)
            else:
                if self.file_hash:
                    if info['hash'] != other.files[path].get('hash'):
                        modified.append(path)
                else:
                    if info['mtime'] != other.files[path].get('mtime'):
                        modified.append(path)
        for path in other.files:
            if path not in self.files:
                removed.append(path)
        return {'added': added, 'modified': modified, 'removed': removed}
