import uuid
import datetime
import copy
import os

class Commit:
    def __init__(self, id, message, parent, sections, locked_sections, collaborators, timestamp=None):
        self.id = id
        self.message = message
        self.parent = parent  # parent commit id or None
        self.sections = copy.deepcopy(sections)
        self.locked_sections = set(locked_sections)
        self.collaborators = set(collaborators)
        self.timestamp = timestamp or datetime.datetime.utcnow()

    def __repr__(self):
        return f"<Commit {self.id}: {self.message}>"

class Repository:
    def __init__(self):
        # Templates storage: name -> {section: template_text}
        self.templates = {}
        # Current working state
        self.sections = {}  # section_name -> content
        self.locked_sections = set()
        self.collaborators = set()
        # Commits and branches
        self.commits = {}
        # Initialize with a root commit "0"
        root = Commit(
            id="0",
            message="root",
            parent=None,
            sections=self.sections,
            locked_sections=self.locked_sections,
            collaborators=self.collaborators,
        )
        self.commits["0"] = root
        self.branches = {"main": "0"}  # branch_name -> head commit id
        self.current_branch = "main"
        self.next_commit_id = 1
        # Snapshots: label -> commit id
        self.snapshots = {}

    # -------------------
    # Template Support
    # -------------------
    def create_template(self, name, template_dict):
        if name in self.templates:
            raise ValueError(f"Template '{name}' already exists.")
        self.templates[name] = copy.deepcopy(template_dict)

    def apply_template(self, name):
        if name not in self.templates:
            raise ValueError(f"Template '{name}' does not exist.")
        tpl = self.templates[name]
        for section, text in tpl.items():
            if section in self.locked_sections:
                raise ValueError(f"Section '{section}' is locked.")
            self.sections[section] = text

    # -------------------
    # Branching
    # -------------------
    def branch(self, new_branch_name):
        if new_branch_name in self.branches:
            raise ValueError(f"Branch '{new_branch_name}' already exists.")
        head = self.branches[self.current_branch]
        self.branches[new_branch_name] = head

    # -------------------
    # Commit
    # -------------------
    def commit(self, message):
        cid = str(self.next_commit_id)
        self.next_commit_id += 1
        parent = self.branches[self.current_branch]
        new_commit = Commit(
            id=cid,
            message=message,
            parent=parent,
            sections=self.sections,
            locked_sections=self.locked_sections,
            collaborators=self.collaborators,
        )
        self.commits[cid] = new_commit
        self.branches[self.current_branch] = cid
        return cid

    # -------------------
    # Log
    # -------------------
    def log(self, branch_name=None):
        bn = branch_name or self.current_branch
        if bn not in self.branches:
            raise ValueError(f"Branch '{bn}' does not exist.")
        commits = []
        cid = self.branches[bn]
        while cid is not None:
            c = self.commits[cid]
            commits.append(c)
            cid = c.parent
        return commits  # newest first

    # -------------------
    # Import
    # -------------------
    def import_section(self, section, file_path):
        if section in self.locked_sections:
            raise ValueError(f"Section '{section}' is locked.")
        if not os.path.isfile(file_path):
            raise ValueError(f"File '{file_path}' does not exist.")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.sections[section] = content

    # -------------------
    # Snapshot
    # -------------------
    def snapshot(self, label):
        if label in self.snapshots:
            raise ValueError(f"Snapshot '{label}' already exists.")
        head = self.branches[self.current_branch]
        self.snapshots[label] = head

    # -------------------
    # Checkout
    # -------------------
    def checkout(self, commit_id_or_label):
        # resolve label
        cid = commit_id_or_label
        if cid in self.snapshots:
            cid = self.snapshots[cid]
        if cid not in self.commits:
            raise ValueError(f"Commit '{commit_id_or_label}' not found.")
        commit = self.commits[cid]
        # restore state
        self.sections = copy.deepcopy(commit.sections)
        self.locked_sections = set(commit.locked_sections)
        self.collaborators = set(commit.collaborators)
        # move HEAD
        self.branches[self.current_branch] = cid

    # -------------------
    # Merge
    # -------------------
    def merge(self, src_branch, dest_branch):
        if src_branch not in self.branches or dest_branch not in self.branches:
            raise ValueError("One or both branches do not exist.")
        head_src = self.branches[src_branch]
        head_dest = self.branches[dest_branch]
        src_commit = self.commits[head_src]
        dest_commit = self.commits[head_dest]
        # start from dest_commit state
        merged_sections = copy.deepcopy(dest_commit.sections)
        merged_locked = set(dest_commit.locked_sections)
        # naive: overwrite or add sections from src
        for sec, txt in src_commit.sections.items():
            if sec in merged_locked:
                continue
            merged_sections[sec] = txt
        # switch to dest branch
        old_branch = self.current_branch
        self.current_branch = dest_branch
        # update working state
        self.sections = merged_sections
        self.locked_sections = merged_locked
        self.collaborators = set(dest_commit.collaborators)
        # perform commit
        merge_msg = f"Merge branch '{src_branch}' into '{dest_branch}'"
        new_cid = self.commit(merge_msg)
        # restore original branch context
        self.current_branch = old_branch
        return new_cid

    # -------------------
    # Collaborators
    # -------------------
    def add_collaborator(self, name):
        if name in self.collaborators:
            raise ValueError(f"Collaborator '{name}' already exists.")
        self.collaborators.add(name)

    def remove_collaborator(self, name):
        if name not in self.collaborators:
            raise ValueError(f"Collaborator '{name}' does not exist.")
        self.collaborators.remove(name)

    def list_collaborators(self):
        return list(self.collaborators)

    # -------------------
    # Lock section
    # -------------------
    def lock_section(self, section):
        self.locked_sections.add(section)
