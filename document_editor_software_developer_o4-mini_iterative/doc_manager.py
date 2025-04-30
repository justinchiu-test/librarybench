class DocumentManager:
    def __init__(self, initial_doc=None):
        self.document = dict(initial_doc) if initial_doc else {}
        self.locked_sections = set()
        self.templates = {}
        self.commit_history = []
        self.activity_feed_list = []
        self.operation_queue = []
        # applied_operations: list of tuples (op_name, args, prev_state)
        self.applied_operations = []
        self.last_autosave = None

    def queue_operation(self, op_name, *args):
        self.operation_queue.append((op_name, args))

    def flush_operations(self):
        """
        Apply all queued operations in order.
        Returns True if operations applied.
        """
        while self.operation_queue:
            op_name, args = self.operation_queue.pop(0)
            method = getattr(self, f"_apply_{op_name}", None)
            if method is None:
                raise AttributeError(f"No apply method for operation '{op_name}'")
            prev_state = method(*args)
            self.applied_operations.append((op_name, args, prev_state))
            self.activity_feed_list.append(f"{op_name} applied: {args}")
        return True

    def edit(self, section, content):
        """Queue an edit operation to update a section."""
        self.queue_operation("edit", section, content)
        self.activity_feed_list.append(f"Queued edit on '{section}'")

    def _apply_edit(self, section, content):
        """Apply edit: returns previous content."""
        if section in self.locked_sections:
            raise RuntimeError(f"Section '{section}' is locked.")
        prev = self.document.get(section)
        self.document[section] = content
        return prev

    def unlock_section(self, section):
        """Queue an unlock_section operation."""
        self.queue_operation("unlock_section", section)
        self.activity_feed_list.append(f"Queued unlock_section on '{section}'")

    def _apply_unlock_section(self, section):
        """Apply unlock: return previous lock state (True if was locked)."""
        prev = section in self.locked_sections
        self.locked_sections.discard(section)
        return prev

    def autosave(self):
        """Periodically autosave current document."""
        self.last_autosave = dict(self.document)
        self.activity_feed_list.append("autosave performed")
        return self.last_autosave

    def commit(self, message):
        """Commit current document state with a message."""
        snapshot = dict(self.document)
        self.commit_history.append((snapshot, message))
        self.activity_feed_list.append(f"commit: '{message}'")
        return True

    def activity_feed(self):
        """Return list of activity feed entries."""
        return list(self.activity_feed_list)

    def version_compare(self, v1, v2):
        """Compare two committed versions; return dict of differences."""
        if v1 < 0 or v1 >= len(self.commit_history) or v2 < 0 or v2 >= len(self.commit_history):
            raise IndexError("Version index out of range")
        doc1, _ = self.commit_history[v1]
        doc2, _ = self.commit_history[v2]
        diffs = {}
        all_keys = set(doc1.keys()) | set(doc2.keys())
        for k in all_keys:
            val1 = doc1.get(k)
            val2 = doc2.get(k)
            if val1 != val2:
                diffs[k] = (val1, val2)
        return diffs

    def resolve_conflict(self, v1, v2):
        """
        Resolve conflicts between two versions by choosing content from version2 for conflicts.
        Merged document replaces current document.
        """
        if v1 < 0 or v1 >= len(self.commit_history) or v2 < 0 or v2 >= len(self.commit_history):
            raise IndexError("Version index out of range")
        doc1, _ = self.commit_history[v1]
        doc2, _ = self.commit_history[v2]
        merged = dict(doc1)
        for k, val2 in doc2.items():
            merged[k] = val2
        self.document = merged
        self.activity_feed_list.append(f"resolve_conflict between {v1} and {v2}")
        return merged

    def undo(self):
        """Undo last applied operation."""
        if not self.applied_operations:
            raise RuntimeError("No operations to undo.")
        op_name, args, prev = self.applied_operations.pop()
        undo_method = getattr(self, f"_undo_{op_name}", None)
        if undo_method is None:
            raise NotImplementedError(f"Undo not implemented for operation '{op_name}'")
        # note: undo methods take prev first, then original args
        undo_method(prev, *args)
        self.activity_feed_list.append(f"undo {op_name}: {args}")
        return True

    def _undo_edit(self, prev, section, content):
        """Undo edit: restore prev content (or remove if None)."""
        if prev is None:
            # section did not exist before
            self.document.pop(section, None)
        else:
            self.document[section] = prev

    def _undo_unlock_section(self, prev, section):
        """Undo unlock_section: restore lock if prev True."""
        if prev:
            self.locked_sections.add(section)

    def create_template(self, name, sections):
        """Create a template with given sections content."""
        if name in self.templates:
            raise ValueError(f"Template '{name}' already exists.")
        self.templates[name] = dict(sections)
        self.activity_feed_list.append(f"create_template '{name}'")

    def apply_template(self, name):
        """Queue apply_template operation to merge template sections."""
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found.")
        self.queue_operation("apply_template", name)
        self.activity_feed_list.append(f"Queued apply_template '{name}'")

    def _apply_apply_template(self, name):
        """Apply template: returns previous document snapshot."""
        prev = dict(self.document)
        sections = self.templates[name]
        for s, c in sections.items():
            if s in self.locked_sections:
                raise RuntimeError(f"Section '{s}' is locked.")
            self.document[s] = c
        return prev

    def _undo_apply_template(self, prev, name):
        """Undo apply_template: restore entire document to prev."""
        self.document = prev
