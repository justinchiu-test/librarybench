import uuid
import datetime
import copy
import os

class Commit:
    def __init__(self, commit_id, message, parents, content):
        self.id = commit_id
        self.message = message
        self.parents = list(parents)  # list of parent IDs
        self.timestamp = datetime.datetime.utcnow()
        # deep copy content to freeze state
        self.content = copy.deepcopy(content)

    def __repr__(self):
        return f"<Commit {self.id[:8]} msg={self.message!r}>"

class Document:
    def __init__(self, name):
        self.name = name
        self.commits = {}
        self.branches = {}
        self.templates = {}      # template_name -> content (string)
        self.snapshots = {}      # label -> commit_id
        self.collaborators = set()
        self.locked_sections = set()

        # create initial commit
        initial_id = self._new_id()
        initial_commit = Commit(initial_id, "Initial commit", [], {})
        self.commits[initial_id] = initial_commit
        # create main branch
        self.branches["main"] = {
            "head": initial_id,
            "working": {}       # section_name -> content
        }

    def _new_id(self):
        return uuid.uuid4().hex

    def _get_branch(self, branch):
        if branch not in self.branches:
            raise ValueError(f"Branch {branch!r} does not exist")
        return self.branches[branch]

    def commit(self, message, branch="main"):
        br = self._get_branch(branch)
        head_id = br["head"]
        head_commit = self.commits[head_id]
        # check locked sections
        working = br["working"]
        for sec in self.locked_sections:
            old = head_commit.content.get(sec)
            new = working.get(sec)
            if old != new:
                raise ValueError(f"Section {sec!r} is locked and cannot be modified")
        # make new commit
        new_id = self._new_id()
        # freeze the current working state as the commit content
        c = Commit(new_id, message, [head_id], working)
        self.commits[new_id] = c
        # advance branch head
        br["head"] = new_id
        # keep working as-is (it already reflects full state)
        return new_id

    def log(self, branch="main"):
        br = self._get_branch(branch)
        out = []
        cur = br["head"]
        while True:
            commit = self.commits[cur]
            out.append({
                "id": commit.id,
                "message": commit.message,
                "timestamp": commit.timestamp
            })
            if not commit.parents:
                break
            # follow first parent
            cur = commit.parents[0]
        return out  # newest first

    def branch(self, new_branch, from_branch="main"):
        if new_branch in self.branches:
            raise ValueError(f"Branch {new_branch!r} already exists")
        src = self._get_branch(from_branch)
        head = src["head"]
        working = copy.deepcopy(self.commits[head].content)
        self.branches[new_branch] = {"head": head, "working": working}

    def create_template(self, name, content):
        self.templates[name] = content

    def apply_template(self, template_name, section_name, branch="main"):
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name!r} does not exist")
        if section_name in self.locked_sections:
            raise ValueError(f"Section {section_name!r} is locked and cannot be modified")
        br = self._get_branch(branch)
        br["working"][section_name] = self.templates[template_name]

    def import_content(self, file_path, section_name, branch="main"):
        if not os.path.isfile(file_path):
            raise ValueError(f"No such file {file_path!r}")
        if section_name in self.locked_sections:
            raise ValueError(f"Section {section_name!r} is locked and cannot be modified")
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        br = self._get_branch(branch)
        br["working"][section_name] = data

    def snapshot(self, label, branch="main"):
        if label in self.snapshots:
            raise ValueError(f"Snapshot label {label!r} already exists")
        head = self._get_branch(branch)["head"]
        self.snapshots[label] = head

    def merge(self, source_branch, dest_branch="main", message=None):
        src = self._get_branch(source_branch)
        dst = self._get_branch(dest_branch)
        src_commit = self.commits[src["head"]]
        dst_commit = self.commits[dst["head"]]

        # build merged content (dst first, then src)
        merged = copy.deepcopy(dst_commit.content)
        merged.update(src_commit.content)

        # honor any locked sections
        for sec in self.locked_sections:
            old = dst_commit.content.get(sec)
            new = merged.get(sec)
            if old != new:
                raise ValueError(f"Section {sec!r} is locked and cannot be modified")

        # create a two‐parent merge commit
        new_id = self._new_id()
        parents = [dst["head"], src["head"]]
        msg = message or f"Merge {source_branch} into {dest_branch}"
        c = Commit(new_id, msg, parents, merged)
        self.commits[new_id] = c

        # advance the destination branch
        dst["head"] = new_id
        dst["working"] = copy.deepcopy(merged)
        return new_id

    def checkout(self, identifier, branch="main"):
        br = self._get_branch(branch)
        # resolve label
        if identifier in self.snapshots:
            cid = self.snapshots[identifier]
        else:
            cid = identifier
        if cid not in self.commits:
            raise ValueError(f"No such commit or snapshot {identifier!r}")
        br["head"] = cid
        br["working"] = copy.deepcopy(self.commits[cid].content)

    def add_collaborator(self, name):
        self.collaborators.add(name)

    def remove_collaborator(self, name):
        if name not in self.collaborators:
            raise ValueError(f"Collaborator {name!r} not found")
        self.collaborators.remove(name)

    def list_collaborators(self):
        # return a sorted list for test consistency
        return sorted(self.collaborators)

    def lock_section(self, section_name):
        self.locked_sections.add(section_name)

    def unlock_section(self, section_name):
        if section_name not in self.locked_sections:
            raise ValueError(f"Section {section_name!r} is not locked")
        self.locked_sections.remove(section_name)
