import time
import uuid
import copy
from enum import Enum


# In-memory registry of documents
_docs = {}


class OperationType(Enum):
    INSERT = "insert"
    EDIT = "edit"
    DELETE = "delete"


class Operation:
    def __init__(self, type, key, value=None, timestamp=None):
        self.type = type
        self.key = key
        self.value = value
        # allow custom timestamp or use current time
        self.timestamp = timestamp if timestamp is not None else time.time()


class Commit:
    def __init__(self, id, message, snapshot, parents):
        self.id = id
        self.message = message
        # deep copy to freeze state
        self.snapshot = copy.deepcopy(snapshot)
        # list of parent commit ids
        self.parents = parents


class Conflict:
    def __init__(self, source_value, dest_value):
        self.source_value = source_value
        self.dest_value = dest_value


class Document:
    def __init__(self, name):
        self.name = name
        # current content key->value
        self.content = {}
        # list of Commit instances in creation order
        self.commits = []
        # mapping branch name -> head commit id
        self.branches = {"main": None}
        self.current_branch = "main"
        self.current_commit_id = None
        # queued operations for real-time edits
        self.operation_queue = []
        # conflicts detected on last merge
        self.conflicts = {}
        # snapshot labels
        self.labels = {}
        # flags
        self.has_uncommitted_changes = False
        # autosave config
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0


def _get_doc(doc_name):
    if doc_name not in _docs:
        raise ValueError(f"Document '{doc_name}' does not exist")
    return _docs[doc_name]


def create_document(name: str):
    """
    Create a new blank document with a 'main' branch.
    """
    doc = Document(name)
    _docs[name] = doc
    return doc


def edit(doc_name: str, key: str, value: str):
    """
    Directly edit the document (immediate change).
    """
    doc = _get_doc(doc_name)
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    # autosave logic
    if doc.autosave_enabled:
        doc.autosave_counter += 1
        if doc.autosave_counter >= doc.autosave_interval:
            # perform autosave commit
            commit(doc_name, "autosave")
            # reset counter
            doc.autosave_counter = 0


def commit(doc_name: str, message: str):
    """
    Commit current state (after syncing any queued ops).
    """
    doc = _get_doc(doc_name)
    # apply any pending operations first
    if doc.operation_queue:
        sync(doc_name)
    # create commit
    new_id = uuid.uuid4().hex
    parents = [doc.current_commit_id] if doc.current_commit_id else []
    commit_obj = Commit(new_id, message, doc.content, parents)
    doc.commits.append(commit_obj)
    doc.current_commit_id = new_id
    # update branch head
    doc.branches[doc.current_branch] = new_id
    doc.has_uncommitted_changes = False
    # after commit, we consider autosave counter reset
    doc.autosave_counter = 0
    return new_id


def log(doc_name: str):
    """
    Return list of commits in reverse order (newest first).
    """
    doc = _get_doc(doc_name)
    # simply return reversed list of commits
    return list(reversed(doc.commits))


def checkout(doc_name: str, commit_or_label: str):
    """
    Checkout to a previous commit by id or snapshot label.
    """
    doc = _get_doc(doc_name)
    # resolve label
    commit_id = commit_or_label
    if commit_or_label in doc.labels:
        commit_id = doc.labels[commit_or_label]
    # find commit
    target = None
    for c in doc.commits:
        if c.id == commit_id:
            target = c
            break
    if target is None:
        raise ValueError(f"Commit '{commit_id}' not found")
    # restore content
    doc.content = copy.deepcopy(target.snapshot)
    doc.current_commit_id = commit_id
    # reset conflicts
    doc.conflicts = {}
    doc.has_uncommitted_changes = False
    # set branch if matches head
    for br, head in doc.branches.items():
        if head == commit_id:
            doc.current_branch = br
            break
    else:
        # default to main if no branch head matches
        doc.current_branch = "main"
    return None


def branch(doc_name: str, branch_name: str):
    """
    Create a new branch pointing to current commit, switch to it.
    """
    doc = _get_doc(doc_name)
    head = doc.current_commit_id
    doc.branches[branch_name] = head
    doc.current_branch = branch_name


def _get_ancestors(doc, commit_id):
    """
    Return set of ancestor commit ids for given commit (including itself).
    """
    seen = set()
    stack = [commit_id] if commit_id else []
    id_map = {c.id: c for c in doc.commits}
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        commit = id_map.get(cid)
        if commit:
            for p in commit.parents:
                if p and p not in seen:
                    stack.append(p)
    return seen


def merge(doc_name: str, source_branch: str, dest_branch: str):
    """
    Merge source_branch into dest_branch with naive conflict detection.
    """
    doc = _get_doc(doc_name)
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        raise ValueError("Branch not found")
    src_id = doc.branches[source_branch]
    dst_id = doc.branches[dest_branch]
    # find common ancestor
    ancestors_src = _get_ancestors(doc, src_id)
    ancestors_dst = _get_ancestors(doc, dst_id)
    common = ancestors_src.intersection(ancestors_dst)
    # pick the nearest common: just pick any, prefer dst or src
    base_id = None
    if common:
        # choose the one with max position in commits list
        for c in reversed(doc.commits):
            if c.id in common:
                base_id = c.id
                break
    # retrieve snapshots
    def snapshot_of(cid):
        if cid is None:
            return {}
        for c in doc.commits:
            if c.id == cid:
                return c.snapshot
        return {}
    base_snap = snapshot_of(base_id)
    src_snap = snapshot_of(src_id)
    dst_snap = snapshot_of(dst_id)
    # perform three-way merge
    merged = {}
    doc.conflicts = {}
    # all keys
    keys = set(base_snap.keys()) | set(src_snap.keys()) | set(dst_snap.keys())
    for key in keys:
        b = base_snap.get(key)
        s = src_snap.get(key)
        d = dst_snap.get(key)
        # conflict if both changed and differ
        if b != s and b != d and s != d:
            # store conflict, keep dest value until resolved
            doc.conflicts[key] = Conflict(s, d)
            if d is not None:
                merged[key] = d
        elif b != s:
            # take source
            if s is not None:
                merged[key] = s
        else:
            # take dest (even if None => deletion)
            if d is not None:
                merged[key] = d
    # apply merge result
    doc.content = merged
    # switch to dest branch
    doc.current_branch = dest_branch
    doc.has_uncommitted_changes = True
    # create merge commit
    merge_msg = f"Merge {source_branch} into {dest_branch}"
    merge_id = commit(doc_name, merge_msg)
    return merge_id


def apply_operation(doc_name: str, op_dict: dict):
    """
    Queue a real-time operation.
    """
    doc = _get_doc(doc_name)
    typ = op_dict.get("type")
    try:
        op_type = OperationType(typ)
    except ValueError:
        # allow uppercase
        op_type = OperationType(typ.lower())
    op = Operation(
        type=op_type,
        key=op_dict.get("key"),
        value=op_dict.get("value"),
    )
    doc.operation_queue.append(op)


def sync(doc_name: str):
    """
    Apply queued operations in timestamp order.
    """
    doc = _get_doc(doc_name)
    ops = sorted(doc.operation_queue, key=lambda o: o.timestamp)
    for op in ops:
        if op.type in (OperationType.INSERT, OperationType.EDIT):
            doc.content[op.key] = op.value
        elif op.type == OperationType.DELETE:
            if op.key in doc.content:
                doc.content.pop(op.key)
    # clear queue
    had_ops = bool(doc.operation_queue)
    doc.operation_queue = []
    if had_ops:
        doc.has_uncommitted_changes = True


def snapshot(doc_name: str, label: str):
    """
    Tag current commit with a human-readable label.
    """
    doc = _get_doc(doc_name)
    cid = doc.current_commit_id
    if cid is None:
        raise ValueError("No commit to snapshot")
    doc.labels[label] = cid
    return cid


def get_conflicts(doc_name: str):
    """
    Return current conflicts mapping key->Conflict.
    """
    doc = _get_doc(doc_name)
    return doc.conflicts


def resolve_conflict(doc_name: str, key: str, resolved_value: str):
    """
    Resolve a merge conflict by setting the final value.
    """
    doc = _get_doc(doc_name)
    if key not in doc.conflicts:
        raise ValueError(f"No conflict for key '{key}'")
    # apply resolution
    doc.content[key] = resolved_value
    # remove conflict record
    doc.conflicts.pop(key, None)
    doc.has_uncommitted_changes = True


def enable_autosave(doc_name: str, interval: int):
    """
    Enable autosave after a number of edits.
    """
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0


def disable_autosave(doc_name: str):
    """
    Disable autosave.
    """
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False
