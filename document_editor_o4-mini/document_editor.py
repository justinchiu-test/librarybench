import time
import uuid
import threading
from enum import Enum
from copy import deepcopy

# Global storage of documents
_documents = {}

class OperationType(Enum):
    INSERT = "insert"
    EDIT = "edit"
    DELETE = "delete"

class Operation:
    def __init__(self, type, key, value=None, timestamp=None):
        self.type = type
        self.key = key
        self.value = value
        self.timestamp = timestamp if timestamp is not None else time.time()

class Conflict:
    def __init__(self, source_value, dest_value):
        self.source_value = source_value
        self.dest_value = dest_value

class Commit:
    def __init__(self, id, message, content_snapshot, parent_ids):
        self.id = id
        self.message = message
        self.content_snapshot = content_snapshot  # dict snapshot
        self.parent_ids = parent_ids  # list of parent commit ids

class Document:
    def __init__(self, name):
        self.name = name
        self.content = {}  # current working content
        self.commits = []  # list of Commit objects
        self.commit_map = {}  # id -> Commit
        self.branches = {"main": None}  # branch name -> head commit id
        self.current_branch = "main"
        self.current_commit_id = None
        self.operation_queue = []
        self.has_uncommitted_changes = False
        self.snapshots = {}  # label -> commit id
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0
        self.conflicts = {}  # key -> Conflict

def _get_doc(doc_name):
    if doc_name not in _documents:
        raise ValueError(f"Document '{doc_name}' does not exist")
    return _documents[doc_name]

def create_document(name: str):
    doc = Document(name)
    _documents[name] = doc
    return doc

def edit(doc_name: str, key: str, value: str):
    doc = _get_doc(doc_name)
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    # autosave handling
    if doc.autosave_enabled:
        doc.autosave_counter += 1
        if doc.autosave_counter >= doc.autosave_interval:
            # perform autosave commit
            # reset counter inside commit
            commit(doc_name, "Autosave")
    return

def _sync(doc):
    if not doc.operation_queue:
        return
    # sort by timestamp
    ops = sorted(doc.operation_queue, key=lambda o: o.timestamp)
    for op in ops:
        if op.type == OperationType.INSERT or op.type == OperationType.EDIT:
            doc.content[op.key] = op.value
        elif op.type == OperationType.DELETE:
            if op.key in doc.content:
                del doc.content[op.key]
    doc.operation_queue.clear()
    doc.has_uncommitted_changes = True

def apply_operation(doc_name: str, operation_dict):
    doc = _get_doc(doc_name)
    typ = operation_dict.get("type")
    if isinstance(typ, str):
        typ = OperationType(typ)
    op = Operation(
        type=typ,
        key=operation_dict.get("key"),
        value=operation_dict.get("value"),
        timestamp=operation_dict.get("timestamp", None),
    )
    doc.operation_queue.append(op)

def sync(doc_name: str):
    doc = _get_doc(doc_name)
    _sync(doc)

def enable_autosave(doc_name: str, interval: int):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0

def disable_autosave(doc_name: str):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False

def snapshot(doc_name: str, label: str):
    doc = _get_doc(doc_name)
    if doc.current_commit_id is None:
        return None
    doc.snapshots[label] = doc.current_commit_id
    return doc.current_commit_id

def log(doc_name: str):
    doc = _get_doc(doc_name)
    # return commits in reverse chronological order
    return list(reversed(doc.commits))

def checkout(doc_name: str, commit_id_or_label: str):
    doc = _get_doc(doc_name)
    cid = commit_id_or_label
    if cid in doc.snapshots:
        cid = doc.snapshots[cid]
    if cid not in doc.commit_map:
        raise ValueError(f"Commit '{cid}' not found")
    commit_obj = doc.commit_map[cid]
    # revert content
    doc.content = deepcopy(commit_obj.content_snapshot)
    doc.current_commit_id = cid
    doc.has_uncommitted_changes = False
    doc.operation_queue.clear()
    # adjust branch if matches head
    for bname, head in doc.branches.items():
        if head == cid:
            doc.current_branch = bname
            break
    return

def branch(doc_name: str, branch_name: str):
    doc = _get_doc(doc_name)
    # set new branch at current commit
    doc.branches[branch_name] = doc.current_commit_id
    doc.current_branch = branch_name

def _get_ancestors(doc, commit_id):
    ancestors = set()
    stack = [commit_id]
    while stack:
        cid = stack.pop()
        if cid is None or cid in ancestors:
            continue
        ancestors.add(cid)
        commit_obj = doc.commit_map.get(cid)
        if commit_obj:
            for p in commit_obj.parent_ids:
                stack.append(p)
    return ancestors

def merge(doc_name: str, source_branch: str, dest_branch: str):
    doc = _get_doc(doc_name)
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        raise ValueError("Branch not found")
    src_cid = doc.branches[source_branch]
    dest_cid = doc.branches[dest_branch]
    # find common ancestor
    src_anc = _get_ancestors(doc, src_cid)
    dest_anc = _get_ancestors(doc, dest_cid)
    commons = src_anc.intersection(dest_anc)
    # pick the nearest common: pick one with max occurrences in doc.commits order
    ancestor = None
    for c in doc.commits:
        if c.id in commons:
            ancestor = c.id
            break
    # get snapshots
    anc_content = {}
    if ancestor:
        anc_content = doc.commit_map[ancestor].content_snapshot
    src_content = {}
    if src_cid:
        src_content = doc.commit_map[src_cid].content_snapshot
    dest_content = {}
    if dest_cid:
        dest_content = doc.commit_map[dest_cid].content_snapshot
    merged = deepcopy(dest_content)
    doc.conflicts.clear()
    keys = set(anc_content.keys()) | set(src_content.keys()) | set(dest_content.keys())
    for key in keys:
        av = anc_content.get(key)
        sv = src_content.get(key)
        dv = dest_content.get(key)
        if sv == dv:
            merged_val = dv
        elif sv == av and dv != av:
            merged_val = dv
        elif dv == av and sv != av:
            merged_val = sv
        else:
            # conflict
            doc.conflicts[key] = Conflict(sv, dv)
            merged_val = dv  # keep dest until resolved
        if merged_val is None:
            if key in merged:
                del merged[key]
        else:
            merged[key] = merged_val
    # apply merge
    doc.content = merged
    doc.has_uncommitted_changes = True
    # perform merge commit
    merge_msg = f"Merge {source_branch} into {dest_branch}"
    new_cid = _commit_internal(doc, merge_msg, parent_ids=[dest_cid, src_cid])
    # update branch pointers
    doc.branches[dest_branch] = new_cid
    doc.current_branch = dest_branch
    doc.current_commit_id = new_cid
    return new_cid

def _commit_internal(doc, message, parent_ids):
    # snapshot current content
    snapshot = deepcopy(doc.content)
    cid = uuid.uuid4().hex
    commit_obj = Commit(cid, message, snapshot, parent_ids)
    doc.commits.append(commit_obj)
    doc.commit_map[cid] = commit_obj
    return cid

def commit(doc_name: str, message: str):
    doc = _get_doc(doc_name)
    # apply queued ops first
    _sync(doc)
    # determine parents
    head = doc.branches.get(doc.current_branch)
    parents = []
    if head:
        parents = [head]
    # create commit
    cid = _commit_internal(doc, message, parents)
    # update branch head and current commit
    doc.branches[doc.current_branch] = cid
    doc.current_commit_id = cid
    doc.has_uncommitted_changes = False
    # reset autosave counter
    doc.autosave_counter = 0
    return cid

def get_conflicts(doc_name: str):
    doc = _get_doc(doc_name)
    return doc.conflicts

def resolve_conflict(doc_name: str, key: str, resolved_value: str):
    doc = _get_doc(doc_name)
    if key in doc.conflicts:
        doc.content[key] = resolved_value
        del doc.conflicts[key]
        doc.has_uncommitted_changes = True
