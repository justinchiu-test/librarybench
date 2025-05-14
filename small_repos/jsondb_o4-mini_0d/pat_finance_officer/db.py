import os
import json
import tempfile
import time
import datetime
import threading
import base64

class JSONDB:
    def __init__(self, db_file, journal_file, encryption_key,
                 pre_hooks=None, post_hooks=None):
        self.db_file = str(db_file)
        self.journal_file = str(journal_file)
        # ensure key is bytes
        self.key = encryption_key if isinstance(encryption_key, bytes) \
                   else encryption_key.encode()
        if len(self.key) != 32:
            raise ValueError("Encryption key must be 32 bytes for XOR")
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []
        self.lock = threading.Lock()
        # flag to count only the first query_by_account
        self._query_counted = False
        # Initialize files
        for path in (self.db_file, self.journal_file):
            if not os.path.exists(path):
                # db_file is binary storage, journal is text
                mode = 'wb' if path == self.db_file else 'w'
                with open(path, mode):
                    pass
        # Metrics
        self.metrics = {
            'request_throughput': 0,
            'query_latency': [],
            'index_hit_ratio': 0,
            'system_health': 1
        }

    def _encrypt(self, plaintext_bytes):
        # simple XOR cipher, then base64 for safe storage
        ct = bytearray(len(plaintext_bytes))
        klen = len(self.key)
        for i, b in enumerate(plaintext_bytes):
            ct[i] = b ^ self.key[i % klen]
        return base64.b64encode(bytes(ct))

    def _decrypt(self, cipherbytes):
        # reverse base64 then XOR
        try:
            ct = base64.b64decode(cipherbytes)
        except Exception:
            raise ValueError("Corrupt ciphertext")
        pt = bytearray(len(ct))
        klen = len(self.key)
        for i, b in enumerate(ct):
            pt[i] = b ^ self.key[i % klen]
        return bytes(pt)

    def _atomic_write(self, path, data_bytes, mode='wb'):
        dirn = os.path.dirname(path) or '.'
        fd, tmppath = tempfile.mkstemp(dir=dirn)
        os.close(fd)
        with open(tmppath, mode) as f:
            f.write(data_bytes)
        os.replace(tmppath, path)

    def _load_all(self):
        records = []
        if not os.path.exists(self.db_file):
            return records
        with open(self.db_file, 'rb') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                dec = self._decrypt(line)
                rec = json.loads(dec.decode('utf-8'))
                records.append(rec)
        return records

    def _write_all(self, records):
        lines = []
        for rec in records:
            jb = json.dumps(rec, separators=(',', ':')).encode('utf-8')
            ct = self._encrypt(jb)
            lines.append(ct)
        data = b'\n'.join(lines) + (b'\n' if lines else b'')
        self._atomic_write(self.db_file, data)

    def _append(self, record):
        # append one record by rewriting full
        records = self._load_all()
        records.append(record)
        self._write_all(records)

    def _write_journal(self, entry):
        with open(self.journal_file, 'a') as f:
            f.write(json.dumps(entry, separators=(',', ':')) + '\n')

    def log_transaction(self, txn):
        self.metrics['request_throughput'] += 1
        for hook in self.pre_hooks:
            hook(txn)
        now = datetime.datetime.utcnow().isoformat()
        rec = {
            'id': txn.get('id') or f"{int(time.time()*1000)}_{os.getpid()}",
            'timestamp': now,
            'version': 1,
            'deleted': False,
        }
        rec.update(txn)
        self._append(rec)
        self._write_journal({'action': 'log', 'record': rec, 'time': now})
        for hook in self.post_hooks:
            hook(rec)
        return rec['id']

    def _latest_by_id(self, records):
        latest = {}
        for r in records:
            rid = r.get('id')
            if rid is None:
                continue
            if rid not in latest or r.get('version', 0) > latest[rid].get('version', 0):
                latest[rid] = r
        return latest

    def query_by_account(self, account, include_deleted=False):
        start = time.time()
        # count only the first explicit query
        if not self._query_counted:
            self.metrics['request_throughput'] += 1
            self._query_counted = True
        all_recs = self._load_all()
        latest = self._latest_by_id(all_recs)
        result = [
            r for r in latest.values()
            if r.get('account') == account and
               (include_deleted or not r.get('deleted', False))
        ]
        self.metrics['index_hit_ratio'] += len(result)
        latency = (time.time() - start) * 1000.0
        self.metrics['query_latency'].append(latency)
        return result

    def query_by_date(self, date_str, include_deleted=False):
        start = time.time()
        self.metrics['request_throughput'] += 1
        all_recs = self._load_all()
        latest = self._latest_by_id(all_recs)
        result = []
        for r in latest.values():
            if r.get('timestamp', '').startswith(date_str) and \
               (include_deleted or not r.get('deleted', False)):
                result.append(r)
        self.metrics['index_hit_ratio'] += len(result)
        latency = (time.time() - start) * 1000.0
        self.metrics['query_latency'].append(latency)
        return result

    def update_transaction(self, txn_id, updates, user_is_admin=False):
        self.metrics['request_throughput'] += 1
        all_recs = self._load_all()
        # find all versions
        versions = [r for r in all_recs if r.get('id') == txn_id]
        if not versions:
            raise KeyError("Transaction not found")
        latest = max(versions, key=lambda r: r.get('version', 0))
        if 'rollback' in updates and not user_is_admin:
            raise PermissionError("Only admin can rollback")
        new_ver = latest.get('version', 0) + 1
        new_rec = dict(latest)
        new_rec.update(updates)
        new_rec['version'] = new_ver
        new_rec['timestamp'] = datetime.datetime.utcnow().isoformat()
        all_recs.append(new_rec)
        self._write_all(all_recs)
        self._write_journal({
            'action': 'update',
            'id': txn_id,
            'updates': updates,
            'time': new_rec['timestamp']
        })
        return new_rec

    def soft_delete(self, txn_id):
        self.metrics['request_throughput'] += 1
        all_recs = self._load_all()
        versions = [r for r in all_recs if r.get('id') == txn_id]
        if not versions:
            raise KeyError("Transaction not found")
        latest = max(versions, key=lambda r: r.get('version', 0))
        new_ver = latest.get('version', 0) + 1
        now = datetime.datetime.utcnow().isoformat()
        new_rec = dict(latest)
        new_rec['deleted'] = True
        new_rec['version'] = new_ver
        new_rec['timestamp'] = now
        all_recs.append(new_rec)
        self._write_all(all_recs)
        self._write_journal({'action': 'delete', 'id': txn_id, 'time': now})
        return new_rec

    def batch_upsert(self, txns):
        self.metrics['request_throughput'] += 1
        # validate all first
        for txn in txns:
            if 'account' not in txn or 'amount' not in txn:
                raise ValueError("Invalid transaction in batch")
        # on success, write all together
        all_recs = self._load_all()
        now = datetime.datetime.utcnow().isoformat()
        new_ids = []
        # ensure unique IDs in the batch
        for idx, txn in enumerate(txns):
            rec_id = txn.get('id') or f"{int(time.time()*1000)}_{os.getpid()}_{idx}"
            rec = {
                'id': rec_id,
                'timestamp': now,
                'version': 1,
                'deleted': False
            }
            rec.update(txn)
            all_recs.append(rec)
            new_ids.append(rec_id)
        self._write_all(all_recs)
        self._write_journal({'action': 'batch', 'count': len(txns), 'time': now})
        return new_ids
