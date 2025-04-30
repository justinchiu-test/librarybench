import difflib

class Document:
    def __init__(self):
        self.sections = {}  # section_name -> text
        self.locked_sections = set()
        self.queued_ops = []  # list of (callable, args)
        self.versions = []  # list of section snapshots
        self.commits = []  # list of (message, version_index)
        self.activity_log = []  # list of strings
        self.templates = {}  # name -> text

    def autosave(self):
        # Flush any pending operations automatically
        self.flush_operations()
        self.activity_log.append("Autosaved document")

    def commit(self, message):
        # Before commit, ensure all ops are applied
        self.flush_operations()
        # Snapshot current sections
        snapshot = self.sections.copy()
        self.versions.append(snapshot)
        version_index = len(self.versions) - 1
        self.commits.append((message, version_index))
        self.activity_log.append(f"Committed version {version_index}: {message}")
        return version_index

    def get_activity_feed(self):
        return list(self.activity_log)

    def version_compare(self, v1, v2):
        if v1 < 0 or v1 >= len(self.versions) or v2 < 0 or v2 >= len(self.versions):
            raise IndexError("Version index out of range")
        doc1 = self.versions[v1]
        doc2 = self.versions[v2]
        # Build comparable text lists with section headers
        text1 = []
        text2 = []
        all_secs = sorted(set(doc1.keys()) | set(doc2.keys()))
        for sec in all_secs:
            text1.append(f"--- {sec} ---")
            text1.extend(doc1.get(sec, "").splitlines())
            text2.append(f"--- {sec} ---")
            text2.extend(doc2.get(sec, "").splitlines())
        diff = difflib.unified_diff(
            text1, text2, fromfile=f"v{v1}", tofile=f"v{v2}", lineterm=""
        )
        return "\n".join(diff)

    def resolve_conflict(self, v1, v2):
        if v1 < 0 or v1 >= len(self.versions) or v2 < 0 or v2 >= len(self.versions):
            raise IndexError("Version index out of range")
        doc1 = self.versions[v1]
        doc2 = self.versions[v2]
        resolved = {}
        conflicts = []
        all_secs = set(doc1.keys()) | set(doc2.keys())
        for sec in all_secs:
            t1 = doc1.get(sec, "")
            t2 = doc2.get(sec, "")
            if t1 == t2:
                resolved[sec] = t1
            else:
                # Create conflict markers
                resolved[sec] = (
                    f"<<<<<<< v{v1}\n"
                    f"{t1}\n"
                    f"=======\n"
                    f"{t2}\n"
                    f">>>>>>> v{v2}"
                )
                conflicts.append(sec)
        self.sections = resolved
        self.activity_log.append(
            f"Resolved conflicts between versions {v1} and {v2} in sections: {', '.join(conflicts)}"
        )
        return conflicts

    def flush_operations(self):
        if not self.queued_ops:
            # Even if no ops, record flush for audit
            self.activity_log.append("Flushed operations")
            return
        for op, args in self.queued_ops:
            op(*args)
        self.queued_ops.clear()
        self.activity_log.append("Flushed operations")

    def edit(self, section, text):
        if section in self.locked_sections:
            raise ValueError(f"Section '{section}' is locked")
        # Schedule the edit
        def _apply(sec, txt):
            self.sections[sec] = txt
        self.queued_ops.append((_apply, (section, text)))
        self.activity_log.append(f"Scheduled edit on section '{section}'")
        # Automatically save after scheduling
        self.autosave()

    def lock_section(self, section):
        self.locked_sections.add(section)
        self.activity_log.append(f"Locked section '{section}'")

    def unlock_section(self, section):
        if section in self.locked_sections:
            self.locked_sections.remove(section)
            self.activity_log.append(f"Unlocked section '{section}'")
        else:
            self.activity_log.append(f"Section '{section}' was not locked")

    def undo(self):
        if not self.versions:
            raise ValueError("No version to revert to")
        last_idx = len(self.versions) - 1
        self.sections = self.versions[last_idx].copy()
        self.activity_log.append(f"Undid to version {last_idx}")

    def create_template(self, name, text):
        self.templates[name] = text
        self.activity_log.append(f"Created template '{name}'")

    def apply_template(self, section, template_name):
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' does not exist")
        tpl_text = self.templates[template_name]
        # Reuse edit (which autosaves)
        self.edit(section, tpl_text)
        self.activity_log.append(f"Applied template '{template_name}' to section '{section}'")
