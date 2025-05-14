import os
import hashlib
from .hash_utils import hash_file

def take_snapshot(directory, filter_func=None):
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            relpath = os.path.relpath(filepath, directory)
            if filter_func and not filter_func(relpath):
                continue
            stat = os.stat(filepath)
            snapshot[relpath] = {
                "size": stat.st_size,
                "mtime": stat.st_mtime,
            }
    return snapshot

def diff_snapshots(old_snap, new_snap, directory=None, hash_compare=False, hash_algo="md5"):
    added = []
    removed = []
    modified = []
    for path in new_snap:
        if path not in old_snap:
            added.append(path)
        else:
            old = old_snap[path]
            new = new_snap[path]
            if old["size"] != new["size"] or abs(old["mtime"] - new["mtime"]) > 1e-6:
                if hash_compare and directory:
                    old_hash = hash_file(os.path.join(directory, path), algorithm=hash_algo)
                    new_hash = hash_file(os.path.join(directory, path), algorithm=hash_algo)
                    if old_hash != new_hash:
                        modified.append(path)
                else:
                    modified.append(path)
    for path in old_snap:
        if path not in new_snap:
            removed.append(path)
    return {"added": added, "removed": removed, "modified": modified}
