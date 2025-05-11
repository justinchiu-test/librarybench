import json
import base64
import threading
import inspect
from datetime import datetime, timedelta

class DocumentStore:
    def __init__(self, encryption_key=None, journaling=False, retention_days=30):
        self.encryption_key = encryption_key
        self.journaling = journaling
        self.retention_days = retention_days
        self.docs = {}
        self.pre_hooks = []
        self.post_hooks = []
        self.journal = []
        self.lock = threading.RLock()

    def _encrypt(self, data):
        raw = json.dumps(data).encode('utf-8')
        payload = base64.b64encode(raw).decode('ascii')
        return {'encrypted': True, 'payload': payload}

    def _decrypt(self, blob):
        if isinstance(blob, dict) and blob.get('encrypted'):
            payload = blob.get('payload')
            raw = base64.b64decode(payload.encode('ascii'))
            return json.loads(raw.decode('utf-8'))
        return blob

    def _apply_pre_hooks(self, document_id, data, operation):
        for hook in self.pre_hooks:
            # call hook with (id, data, op) if it accepts 3 args, else with (id, data)
            sig = inspect.signature(hook)
            # count non-varargs positional parameters
            pos_params = [
                p for p in sig.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
            if len(pos_params) >= 3:
                hook(document_id, data, operation)
            elif len(pos_params) >= 2:
                hook(document_id, data)
            else:
                # fallback: try calling with two args
                hook(document_id, data)

    def _apply_post_hooks(self, document_id, data, operation):
        for hook in self.post_hooks:
            sig = inspect.signature(hook)
            pos_params = [
                p for p in sig.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
            if len(pos_params) >= 3:
                hook(document_id, data, operation)
            elif len(pos_params) >= 2:
                hook(document_id, data)
            else:
                hook(document_id, data)

    def register_pre_hook(self, func):
        self.pre_hooks.append(func)

    def register_post_hook(self, func):
        self.post_hooks.append(func)

    def create(self, document_id, data):
        with self.lock:
            if document_id in self.docs and not self._is_deleted(document_id):
                raise ValueError("Document already exists")
            # hooks
            self._apply_pre_hooks(document_id, data, 'create')
            version = 1
            entry = {
                'version': version,
                'timestamp': datetime.utcnow(),
                'data': self._encrypt(data) if self.encryption_key else data,
                'deleted': False
            }
            self.docs[document_id] = [entry]
            if self.journaling:
                self.journal.append(('create', document_id, version, data))
            self._apply_post_hooks(document_id, data, 'create')
            return version

    def read(self, document_id, version=None):
        with self.lock:
            if document_id not in self.docs:
                raise KeyError("Document not found")
            versions = self.docs[document_id]
            if version is None:
                entry = versions[-1]
            else:
                found = [e for e in versions if e['version'] == version]
                if not found:
                    raise KeyError("Version not found")
                entry = found[0]
            if entry['deleted']:
                raise KeyError("Document is deleted")
            data = entry['data']
            return self._decrypt(data)

    def update(self, document_id, patch):
        with self.lock:
            if document_id not in self.docs:
                raise KeyError("Document not found")
            current = self.docs[document_id][-1]
            if current['deleted']:
                raise KeyError("Document is deleted")
            existing_data = self._decrypt(current['data'])
            merged = existing_data.copy()
            merged.update(patch)
            self._apply_pre_hooks(document_id, merged, 'update')
            version = current['version'] + 1
            entry = {
                'version': version,
                'timestamp': datetime.utcnow(),
                'data': self._encrypt(merged) if self.encryption_key else merged,
                'deleted': False
            }
            self.docs[document_id].append(entry)
            if self.journaling:
                self.journal.append(('update', document_id, version, patch))
            self._apply_post_hooks(document_id, merged, 'update')
            return version

    def delete(self, document_id):
        with self.lock:
            if document_id not in self.docs:
                raise KeyError("Document not found")
            current = self.docs[document_id][-1]
            if current['deleted']:
                raise KeyError("Already deleted")
            # pre hook with None data
            self._apply_pre_hooks(document_id, None, 'delete')
            version = current['version'] + 1
            entry = {
                'version': version,
                'timestamp': datetime.utcnow(),
                'data': current['data'],
                'deleted': True
            }
            self.docs[document_id].append(entry)
            if self.journaling:
                self.journal.append(('delete', document_id, version, None))
            self._apply_post_hooks(document_id, None, 'delete')
            return version

    def _is_deleted(self, document_id):
        return self.docs[document_id][-1]['deleted']

    def rollback(self, document_id, version):
        with self.lock:
            if document_id not in self.docs:
                raise KeyError("Document not found")
            versions = self.docs[document_id]
            found = [e for e in versions if e['version'] == version]
            if not found:
                raise KeyError("Version not found")
            target = found[0]
            if target['deleted']:
                raise ValueError("Cannot rollback to deleted version")
            data = self._decrypt(target['data'])
            self._apply_pre_hooks(document_id, data, 'rollback')
            new_version = versions[-1]['version'] + 1
            entry = {
                'version': new_version,
                'timestamp': datetime.utcnow(),
                'data': target['data'],
                'deleted': False
            }
            self.docs[document_id].append(entry)
            if self.journaling:
                self.journal.append(('rollback', document_id, new_version, {'to': version}))
            self._apply_post_hooks(document_id, data, 'rollback')
            return new_version

    def batch_upsert(self, items):
        with self.lock:
            # make a deep-ish copy of the version lists to rollback on failure
            orig_docs = {doc: list(vers) for doc, vers in self.docs.items()}
            new_versions = {}
            try:
                for document_id, data in items:
                    if document_id in self.docs and not self._is_deleted(document_id):
                        v = self.update(document_id, data)
                    else:
                        v = self.create(document_id, data)
                    new_versions[document_id] = v
                return new_versions
            except Exception:
                # rollback state
                self.docs = orig_docs
                raise

    def purge(self):
        with self.lock:
            now = datetime.utcnow()
            to_delete = []
            for doc_id, versions in list(self.docs.items()):
                last = versions[-1]
                if last['deleted']:
                    delta = now - last['timestamp']
                    if delta > timedelta(days=self.retention_days):
                        to_delete.append(doc_id)
            for doc_id in to_delete:
                del self.docs[doc_id]
