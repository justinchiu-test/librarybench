import copy
import datetime
import difflib


class DocumentError(Exception):
    pass


class ConflictError(DocumentError):
    pass


class Document:
    def __init__(self, doc_id, initial_sections):
        self.doc_id = doc_id
        # Current live content of sections
        self.sections = dict(initial_sections)
        # List of versions: each is a dict with keys 'content', 'message', 'timestamp'
        # The initial version has message 'init'
        init_version = {
            'content': copy.deepcopy(self.sections),
            'message': 'init',
            'timestamp': datetime.datetime.utcnow(),
        }
        self.versions = [init_version]
        # Pending operations queue: list of tuples (op_type, args...)
        self.pending_ops = []
        # Locked sections
        self.locks = set()
        # Conflicted sections
        self.conflicts = set()


class DocumentManager:
    def __init__(self):
        # Map of doc_id -> Document
        self.documents = {}
        # Global activity feed: list of dict entries
        self.activity_feed = []
        # Templates: name -> content
        self.templates = {}

    def _log_activity(self, doc_id, operation, details=None):
        entry = {
            'timestamp': datetime.datetime.utcnow(),
            'doc_id': doc_id,
            'operation': operation,
            'details': details or {}
        }
        self.activity_feed.append(entry)

    def create_document(self, doc_id, initial_sections):
        if doc_id in self.documents:
            raise DocumentError(f"Document {doc_id} already exists")
        self.documents[doc_id] = Document(doc_id, initial_sections)
        self._log_activity(doc_id, 'create_document', {'sections': list(initial_sections.keys())})

    def autosave(self, doc_id, section, content):
        doc = self._get_doc(doc_id)
        # behave like edit but tagged autosave
        self._queue_edit(doc, section, content, op_type='autosave')

    def edit(self, doc_id, section, content):
        doc = self._get_doc(doc_id)
        self._queue_edit(doc, section, content, op_type='edit')

    def _queue_edit(self, doc, section, content, op_type):
        if section in doc.locks:
            # conflict
            doc.conflicts.add(section)
            self._log_activity(doc.doc_id, 'conflict', {'section': section})
            raise ConflictError(f"Section '{section}' is locked; conflict occurred")
        # Lock the section for exclusive editing
        doc.locks.add(section)
        # Queue the operation
        doc.pending_ops.append((op_type, section, content))
        self._log_activity(doc.doc_id, f'{op_type}_queued', {'section': section})

    def flush_operations(self, doc_id):
        doc = self._get_doc(doc_id)
        for op_type, section, content in doc.pending_ops:
            # Apply the change
            doc.sections[section] = content
            self._log_activity(doc.doc_id, f'{op_type}_flushed', {'section': section})
        doc.pending_ops.clear()

    def commit(self, doc_id, message):
        doc = self._get_doc(doc_id)
        # First apply pending ops
        self.flush_operations(doc_id)
        # Take snapshot
        snapshot = copy.deepcopy(doc.sections)
        version = {
            'content': snapshot,
            'message': message,
            'timestamp': datetime.datetime.utcnow()
        }
        doc.versions.append(version)
        # Clear locks and conflicts
        doc.locks.clear()
        doc.conflicts.clear()
        self._log_activity(doc_id, 'commit', {'message': message, 'version': len(doc.versions)})

    def activity_feed_all(self):
        return list(self.activity_feed)

    def version_compare(self, doc_id, v1, v2):
        doc = self._get_doc(doc_id)
        if v1 < 1 or v2 < 1 or v1 > len(doc.versions) or v2 > len(doc.versions):
            raise DocumentError("Invalid version numbers")
        c1 = doc.versions[v1 - 1]['content']
        c2 = doc.versions[v2 - 1]['content']
        all_sections = set(c1.keys()) | set(c2.keys())
        diffs = {}
        for sec in all_sections:
            s1 = c1.get(sec, "").splitlines(keepends=True)
            s2 = c2.get(sec, "").splitlines(keepends=True)
            diff = list(difflib.unified_diff(s1, s2, fromfile=f'v{v1}/{sec}', tofile=f'v{v2}/{sec}', lineterm=''))
            diffs[sec] = diff
        self._log_activity(doc_id, 'version_compare', {'v1': v1, 'v2': v2})
        return diffs

    def resolve_conflict(self, doc_id, section, resolution_content):
        doc = self._get_doc(doc_id)
        if section not in doc.conflicts:
            raise DocumentError(f"No conflict to resolve for section '{section}'")
        # Overwrite with resolution
        doc.sections[section] = resolution_content
        doc.conflicts.discard(section)
        # Also clear lock
        doc.locks.discard(section)
        self._log_activity(doc_id, 'resolve_conflict', {'section': section})

    def unlock_section(self, doc_id, section):
        doc = self._get_doc(doc_id)
        if section in doc.locks:
            doc.locks.remove(section)
            self._log_activity(doc_id, 'unlock_section', {'section': section})

    def undo(self, doc_id):
        doc = self._get_doc(doc_id)
        # If pending operations exist, drop the last one
        if doc.pending_ops:
            op = doc.pending_ops.pop()
            op_type, section, _ = op
            # Also unlock if it was locked
            doc.locks.discard(section)
            self._log_activity(doc.doc_id, 'undo_pending', {'op_type': op_type, 'section': section})
            return

        # Else, undo last commit if more than 1 version
        if len(doc.versions) > 1:
            # Remove last version
            removed = doc.versions.pop()
            # Revert sections to the new last version
            doc.sections = copy.deepcopy(doc.versions[-1]['content'])
            # Clear locks and conflicts
            doc.locks.clear()
            doc.conflicts.clear()
            self._log_activity(doc.doc_id, 'undo_commit', {'restored_to_version': len(doc.versions)})
            return

        raise DocumentError("Nothing to undo")

    def create_template(self, name, content):
        if name in self.templates:
            raise DocumentError(f"Template '{name}' already exists")
        self.templates[name] = content
        # No doc_id here, global operation
        self._log_activity(None, 'create_template', {'name': name})

    def apply_template(self, doc_id, section, template_name):
        if template_name not in self.templates:
            raise DocumentError(f"Template '{template_name}' not found")
        content = self.templates[template_name]
        doc = self._get_doc(doc_id)
        if section in doc.locks:
            doc.conflicts.add(section)
            self._log_activity(doc_id, 'conflict', {'section': section})
            raise ConflictError(f"Section '{section}' is locked; conflict occurred")
        doc.locks.add(section)
        doc.pending_ops.append(('apply_template', section, content))
        self._log_activity(doc_id, 'apply_template_queued', {'section': section, 'template': template_name})

    def _get_doc(self, doc_id):
        if doc_id not in self.documents:
            raise DocumentError(f"Document '{doc_id}' does not exist")
        return self.documents[doc_id]
