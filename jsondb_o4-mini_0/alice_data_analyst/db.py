import os
import json
import uuid
import shutil
from threading import RLock
from encryption import Encryption

class Database:
    def __init__(self, path, key, metrics, hooks):
        self.path = path
        self.enc = Encryption(key)
        self.metrics = metrics
        self.hooks = hooks
        self.lock = RLock()
        os.makedirs(self._events_dir(), exist_ok=True)
        os.makedirs(self._versions_dir(), exist_ok=True)
        os.makedirs(self._journal_dir(), exist_ok=True)
        self.journal_file = os.path.join(self._journal_dir(), 'journal.log')
        # default hooks
        from datetime import datetime
        def normalize_ts(data):
            if 'timestamp' in data:
                try:
                    dt = datetime.fromisoformat(data['timestamp'])
                    data['timestamp'] = dt.isoformat()
                except Exception:
                    pass
        self.hooks.register_pre(normalize_ts)
        def mark_normalized(data):
            data['normalized'] = True
        self.hooks.register_post(mark_normalized)

    def _events_dir(self):
        return os.path.join(self.path, 'events')

    def _versions_dir(self):
        return os.path.join(self.path, 'versions')

    def _journal_dir(self):
        return os.path.join(self.path, 'journal')

    def _event_file(self, id):
        return os.path.join(self._events_dir(), f"{id}.json.enc")

    def _version_dir(self, id):
        return os.path.join(self._versions_dir(), id)

    def _version_file(self, id, ver):
        return os.path.join(self._version_dir(id), f"{ver}.json.enc")

    def _write_file_atomic(self, filepath, data_bytes):
        tmp = filepath + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(data_bytes)
        os.replace(tmp, filepath)

    def _journal(self, entry):
        with open(self.journal_file, 'a') as f:
            f.write(json.dumps(entry))
            f.write("\n")

    def insert_event(self, data):
        with self.lock:
            data = dict(data)
            self.hooks.run_pre(data)
            id_ = data.get('id') or str(uuid.uuid4())
            data['id'] = id_
            from datetime import datetime
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
            data['deleted'] = False
            data['version'] = 1
            # run post hooks now so normalized flag is persisted
            self.hooks.run_post(data)
            raw = json.dumps(data).encode()
            enc = self.enc.encrypt(raw)
            evpath = self._event_file(id_)
            self._write_file_atomic(evpath, enc)
            vdir = self._version_dir(id_)
            os.makedirs(vdir, exist_ok=True)
            vpath = self._version_file(id_, 1)
            self._write_file_atomic(vpath, enc)
            self._journal({'op': 'insert', 'id': id_, 'version': 1})
            if 'campaign' in data:
                self.metrics.increment(f"campaign_{data['campaign']}")
            return data

    def get_event(self, id):
        path = self._event_file(id)
        if not os.path.exists(path):
            return None
        enc = open(path, 'rb').read()
        raw = self.enc.decrypt(enc)
        return json.loads(raw)

    def update_event(self, id, fields):
        with self.lock:
            ev = self.get_event(id)
            if not ev:
                return None
            self.hooks.run_pre(fields)
            ev.update(fields)
            ev['version'] = ev.get('version', 1) + 1
            # run post hooks now so normalized flag is persisted
            self.hooks.run_post(ev)
            raw = json.dumps(ev).encode()
            enc = self.enc.encrypt(raw)
            self._write_file_atomic(self._event_file(id), enc)
            vdir = self._version_dir(id)
            os.makedirs(vdir, exist_ok=True)
            vpath = self._version_file(id, ev['version'])
            self._write_file_atomic(vpath, enc)
            self._journal({'op': 'update', 'id': id, 'version': ev['version'], 'fields': fields})
            return ev

    def soft_delete(self, id):
        with self.lock:
            ev = self.get_event(id)
            if not ev or ev.get('deleted'):
                return False
            ev['deleted'] = True
            ev['version'] = ev.get('version', 1) + 1
            # run post hooks now
            self.hooks.run_post(ev)
            raw = json.dumps(ev).encode()
            enc = self.enc.encrypt(raw)
            self._write_file_atomic(self._event_file(id), enc)
            vdir = self._version_dir(id)
            os.makedirs(vdir, exist_ok=True)
            vpath = self._version_file(id, ev['version'])
            self._write_file_atomic(vpath, enc)
            self._journal({'op': 'soft_delete', 'id': id, 'version': ev['version']})
            return True

    def undelete_event(self, id):
        with self.lock:
            ev = self.get_event(id)
            if not ev or not ev.get('deleted'):
                return False
            ev['deleted'] = False
            ev['version'] = ev.get('version', 1) + 1
            self.hooks.run_post(ev)
            raw = json.dumps(ev).encode()
            enc = self.enc.encrypt(raw)
            self._write_file_atomic(self._event_file(id), enc)
            vdir = self._version_dir(id)
            os.makedirs(vdir, exist_ok=True)
            vpath = self._version_file(id, ev['version'])
            self._write_file_atomic(vpath, enc)
            self._journal({'op': 'undelete', 'id': id, 'version': ev['version']})
            return True

    def purge_event(self, id):
        with self.lock:
            path = self._event_file(id)
            if not os.path.exists(path):
                return False
            os.remove(path)
            vdir = self._version_dir(id)
            if os.path.exists(vdir):
                shutil.rmtree(vdir)
            self._journal({'op': 'purge', 'id': id})
            return True

    def get_versions(self, id):
        vdir = self._version_dir(id)
        if not os.path.exists(vdir):
            return None
        files = [f for f in os.listdir(vdir) if f.endswith('.json.enc')]
        vers = sorted(int(f.split('.')[0]) for f in files)
        return vers

    def restore_version(self, id, ver):
        with self.lock:
            vfile = self._version_file(id, ver)
            if not os.path.exists(vfile):
                return None
            enc = open(vfile, 'rb').read()
            raw = self.enc.decrypt(enc)
            data = json.loads(raw)
            # compute new version as max existing + 1
            existing = self.get_versions(id) or []
            maxv = max(existing) if existing else ver
            newver = maxv + 1
            data['version'] = newver
            # run post hooks so normalized if needed
            self.hooks.run_post(data)
            raw2 = json.dumps(data).encode()
            enc2 = self.enc.encrypt(raw2)
            self._write_file_atomic(self._event_file(id), enc2)
            vdir = self._version_dir(id)
            os.makedirs(vdir, exist_ok=True)
            vpath = self._version_file(id, data['version'])
            self._write_file_atomic(vpath, enc2)
            self._journal({'op': 'restore', 'id': id, 'from': ver, 'to': data['version']})
            return data

    def query(self, campaign=None, start=None, end=None):
        result = []
        for fname in os.listdir(self._events_dir()):
            if not fname.endswith('.json.enc'):
                continue
            id_ = fname[:-9]
            ev = self.get_event(id_)
            if not ev or ev.get('deleted'):
                continue
            if campaign and ev.get('campaign') != campaign:
                continue
            if start or end:
                from datetime import datetime
                dt = datetime.fromisoformat(ev.get('timestamp'))
                if start:
                    if dt < datetime.fromisoformat(start):
                        continue
                if end:
                    if dt > datetime.fromisoformat(end):
                        continue
            result.append(ev)
        return result

    def batch_upsert(self, events):
        with self.lock:
            results = []
            for ev in events:
                # insert_event now uses RLock, so reentrancy is allowed
                results.append(self.insert_event(ev))
            return results
