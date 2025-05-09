import copy

class Document:
    """
    A class to manage design documents with versioning, branching, collaboration, and templates.
    """
    # Predefined templates
    templates = {
        "simple": {"header": "Header", "footer": "Footer"},
        "full": {"header": "Full Header", "body": "Body", "footer": "Full Footer"},
    }

    def __init__(self, branch_name="main"):
        # The actual content of the document: section_name -> text
        self.content = {}
        # Sections that are locked (cannot be edited)
        self.locked_sections = set()
        # Collaborators on this document
        self.collaborators = set()
        # History: list of dicts {operation, details, content_snapshot}
        self.history = []
        # For redo: stack of content snapshots undone via checkout
        self.redo_history = []
        # Name of this branch/document copy
        self.branch_name = branch_name
        # Current version pointer is always the last history entry
        self.current_version = 0

        # Initialize history with the empty document
        self._record_history("init", {"branch": self.branch_name})

    def _record_history(self, operation, details):
        """
        Record an operation in history along with a snapshot of content.
        """
        snapshot = copy.deepcopy(self.content)
        entry = {
            "operation": operation,
            "details": details,
            "content": snapshot
        }
        self.history.append(entry)
        self.current_version = len(self.history) - 1

    def unlock_section(self, section):
        """
        Unlock a section so it can be edited.
        """
        self.locked_sections.discard(section)
        self._record_history("unlock_section", {"section": section})
    
    def edit(self, section, new_content):
        """
        Update or create a section's content. Raises if section is locked.
        """
        if section in self.locked_sections:
            raise ValueError(f"Section '{section}' is locked and cannot be edited.")
        self.content[section] = new_content
        # Clear redo history on new edit
        self.redo_history.clear()
        self._record_history("edit", {"section": section, "content": new_content})

    def add_collaborator(self, name):
        """
        Add a collaborator.
        """
        self.collaborators.add(name)
        self._record_history("add_collaborator", {"name": name})

    def remove_collaborator(self, name):
        """
        Remove a collaborator (no-op if not present).
        """
        self.collaborators.discard(name)
        self._record_history("remove_collaborator", {"name": name})

    def collaborator_list(self):
        """
        Return the list of collaborators.
        """
        return list(self.collaborators)

    def history_view(self):
        """
        Return the list of history entries (operation + details).
        """
        # Return shallow copies so external code doesn't mutate internal history
        return [
            {"operation": entry["operation"], "details": copy.deepcopy(entry["details"])}
            for entry in self.history
        ]

    def apply_operation(self, operation):
        """
        Simulate an operation on the document content without committing it.
        Returns the new simulated content.
        """
        temp = copy.deepcopy(self.content)
        result = operation(temp)
        return result

    @staticmethod
    def resolve_conflict(changes1, changes2):
        """
        Merge two sets of changes (dicts). Last-write-wins for overlapping sections.
        """
        merged = changes1.copy()
        merged.update(changes2)
        return merged

    def template_support(self, template_name):
        """
        Apply a predefined template to the document content.
        """
        if template_name not in Document.templates:
            raise ValueError(f"Template '{template_name}' does not exist.")
        self.content.update(Document.templates[template_name])
        # Clear redo on template application
        self.redo_history.clear()
        self._record_history("template_support", {"template": template_name})

    def checkout(self, version_index):
        """
        Revert the document content to a previous version.
        """
        if not (0 <= version_index < len(self.history)):
            raise IndexError("Version index out of range.")
        # Save current content to redo stack
        self.redo_history.append(copy.deepcopy(self.content))
        # Perform checkout
        target_snapshot = self.history[version_index]["content"]
        self.content = copy.deepcopy(target_snapshot)
        self._record_history("checkout", {"version": version_index})

    def redo(self):
        """
        Reapply the last undone change (from checkout).
        """
        if not self.redo_history:
            raise IndexError("No operation to redo.")
        new_snapshot = self.redo_history.pop()
        self.content = copy.deepcopy(new_snapshot)
        self._record_history("redo", {})

    def branch(self, new_branch_name):
        """
        Create a branch (clone) of this document. Returns the new Document.
        """
        doc_copy = copy.deepcopy(self)
        doc_copy.branch_name = new_branch_name
        doc_copy._record_history("branch", {"from": self.branch_name, "to": new_branch_name})
        return doc_copy
