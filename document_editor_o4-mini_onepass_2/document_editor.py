import uuid
import time
import threading
from enum import Enum
from copy import deepcopy

# In-memory registry of documents
_docs = {}

class OperationType(Enum):
    INSERT = "insert"
    EDIT = "edit"
    DELETE = "delete"

class Operation:
    def __init__(self, type, key, value=None, timestamp=None):
        # type: OperationType
        self.type = type
        self.key = key
        self.value = value
        self.timestamp = timestamp if timestamp is not None else time.time()

class Conflict:
    def __init__(self, source_value, dest_value):
        self.source_value = source_value
        self.dest_value = dest_value

class Commit:
    def __init__(self, id, message, content_snapshot, parents, branch):
        self.id = id
        self.message = message
        self.content = content_snapshot  # dict snapshot
        self.parents = parents  # list of parent commit ids
        self.branch = branch
        self.timestamp = time.time()

class Document:
    def __init__(self, name):
        self.name = name
        self.content = {}  # current working content
        self.commits = []  # list of Commit objects (chronological)
        self.commits_by_id = {}  # id -> Commit
        self.current_branch = "main"
        self.branches = {"main": None}  # branch name -> commit id
        self.current_commit_id = None
        self.operation_queue = []  # list of Operation
        self.has_uncommitted_changes = False
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0
        self.snapshots = {}  # label -> commit id
        self.conflicts = {}  # key -> Conflict

def _get_doc(doc_name):
    if doc_name not in _docs:
        raise ValueError(f"Document '{doc_name}' does not exist")
    return _docs[doc_name]

def create_document(name: str):
    """Create a new blank document."""
    doc = Document(name)
    _docs[name] = doc
    return doc

def edit(doc_name: str, key: str, value: str):
    """Update content under key."""
    doc = _get_doc(doc_name)
    # Apply edit immediately
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    # Autosave logic
    if doc.autosave_enabled:
        doc.autosave_counter += 1
        if doc.autosave_counter >= doc.autosave_interval:
            # perform autosave commit
            commit(doc_name, "autosave")
            # commit resets autosave_counter
    return

def apply_operation(doc_name: str, op_dict: dict):
    """Queue an operation for real-time edits."""
    doc = _get_doc(doc_name)
    typ = op_dict.get("type")
    # map to OperationType
    if isinstance(typ, OperationType):
        op_type = typ
    else:
        op_type = OperationType(typ)
    op = Operation(
        type=op_type,
        key=op_dict.get("key"),
        value=op_dict.get("value"),
        timestamp=op_dict.get("timestamp", None),
    )
    doc.operation_queue.append(op)
    return

def sync(doc_name: str):
    """Apply queued operations in timestamp order."""
    doc = _get_doc(doc_name)
    if not doc.operation_queue:
        return
    # sort by timestamp
    doc.operation_queue.sort(key=lambda o: o.timestamp)
    for op in doc.operation_queue:
        if op.type == OperationType.DELETE:
            if op.key in doc.content:
                del doc.content[op.key]
        elif op.type in (OperationType.INSERT, OperationType.EDIT):
            doc.content[op.key] = op.value
    doc.operation_queue.clear()
    doc.has_uncommitted_changes = True
    return

def commit(doc_name: str, message: str):
    """Commit current state with message."""
    doc = _get_doc(doc_name)
    # apply queued operations first
    sync(doc_name)
    # snapshot content
    snapshot = deepcopy(doc.content)
    commit_id = str(uuid.uuid4())
    parents = []
    if doc.current_commit_id is not None:
        parents.append(doc.current_commit_id)
    new_commit = Commit(
        id=commit_id,
        message=message,
        content_snapshot=snapshot,
        parents=parents,
        branch=doc.current_branch,
    )
    doc.commits.append(new_commit)
    doc.commits_by_id[commit_id] = new_commit
    doc.current_commit_id = commit_id
    # update branch head
    doc.branches[doc.current_branch] = commit_id
    # reset flags
    doc.has_uncommitted_changes = False
    doc.autosave_counter = 0
    return commit_id

def log(doc_name: str):
    """Return commit history (latest first)."""
    doc = _get_doc(doc_name)
    # Return commits in reverse chronological order
    return list(reversed(doc.commits))

def checkout(doc_name: str, commit_ref: str):
    """Revert to a previous commit by id or label."""
    doc = _get_doc(doc_name)
    # resolve label
    commit_id = None
    if commit_ref in doc.snapshots:
        commit_id = doc.snapshots[commit_ref]
    else:
        commit_id = commit_ref
    if commit_id not in doc.commits_by_id:
        raise ValueError(f"Commit '{commit_ref}' not found")
    # restore content
    commit_obj = doc.commits_by_id[commit_id]
    doc.content = deepcopy(commit_obj.content)
    doc.current_commit_id = commit_id
    # clear conflicts and queue
    doc.conflicts.clear()
    doc.operation_queue.clear()
    doc.has_uncommitted_changes = False
    # detect branch switch
    for br, head in doc.branches.items():
        if head == commit_id:
            doc.current_branch = br
            break
    return

def branch(doc_name: str, branch_name: str):
    """Fork current state into a new branch."""
    doc = _get_doc(doc_name)
    if branch_name in doc.branches:
        raise ValueError(f"Branch '{branch_name}' already exists")
    # new branch points to current commit
    doc.branches[branch_name] = doc.current_commit_id
    doc.current_branch = branch_name
    return

def _find_common_ancestor(doc, commit_a, commit_b):
    # collect ancestors of a
    visited = set()
    stack = [commit_a]
    while stack:
        cid = stack.pop()
        if cid is None:
            continue
        if cid in visited:
            continue
        visited.add(cid)
        cobj = doc.commits_by_id.get(cid)
        if cobj:
            for p in cobj.parents:
                stack.append(p)
    # walk b's ancestors
    stack = [commit_b]
    while stack:
        cid = stack.pop()
        if cid is None:
            continue
        if cid in visited:
            return cid
        cobj = doc.commits_by_id.get(cid)
        if cobj:
            for p in cobj.parents:
                stack.append(p)
    return None

def merge(doc_name: str, source_branch: str, dest_branch: str):
    """Naive merge with conflict detection."""
    doc = _get_doc(doc_name)
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        raise ValueError("Invalid branch name")
    src_commit = doc.branches[source_branch]
    dst_commit = doc.branches[dest_branch]
    # find common ancestor
    ancestor = _find_common_ancestor(doc, src_commit, dst_commit)
    ancestor_content = {}
    if ancestor:
        ancestor_content = doc.commits_by_id[ancestor].content
    src_content = {}
    if src_commit:
        src_content = doc.commits_by_id[src_commit].content
    dst_content = {}
    if dst_commit:
        dst_content = doc.commits_by_id[dst_commit].content
    # prepare merge
    merged = deepcopy(dst_content)
    # clear old conflicts
    doc.conflicts.clear()
    # all keys
    keys = set(ancestor_content.keys()) | set(src_content.keys()) | set(dst_content.keys())
    for key in keys:
        anc = ancestor_content.get(key)
        sv = src_content.get(key)
        dv = dst_content.get(key)
        changed_src = sv != anc
        changed_dst = dv != anc
        # conflict
        if changed_src and changed_dst and sv != dv:
            # register conflict, keep dest until resolution
            doc.conflicts[key] = Conflict(source_value=sv, dest_value=dv)
            merged[key] = dv
        else:
            # no conflict: if src changed, take src; else keep dest
            if changed_src:
                merged[key] = sv
            else:
                # if key deleted in src and not changed in dst?
                if key not in dst_content and key in merged:
                    merged.pop(key, None)
                # else keep existing dst
                pass
    # apply merged
    doc.content = merged
    doc.current_branch = dest_branch
    # commit merge
    merge_msg = f"Merge {source_branch} into {dest_branch}"
    # manual injection of two parents
    # temporarily override commit parents logic
    # commit() uses only single parent; adjust after commit
    merge_id = commit(doc_name, merge_msg)
    # override parents for merge commit
    merge_commit = doc.commits_by_id[merge_id]
    merge_commit.parents = [dst_commit, src_commit]
    # update branch head
    doc.branches[dest_branch] = merge_id
    return merge_id

def get_conflicts(doc_name: str):
    """Return current conflicts dict."""
    doc = _get_doc(doc_name)
    return doc.conflicts

def resolve_conflict(doc_name: str, key: str, resolved_value: str):
    """Resolve a conflict by choosing resolved_value."""
    doc = _get_doc(doc_name)
    if key not in doc.conflicts:
        raise ValueError(f"No conflict for key '{key}'")
    # apply resolution
    doc.content[key] = resolved_value
    # remove conflict
    del doc.conflicts[key]
    doc.has_uncommitted_changes = True
    return

def snapshot(doc_name: str, label: str):
    """Tag a specific version with a label."""
    doc = _get_doc(doc_name)
    if doc.current_commit_id is None:
        raise ValueError("No commit to snapshot")
    doc.snapshots[label] = doc.current_commit_id
    return doc.current_commit_id

def enable_autosave(doc_name: str, interval: int):
    """Enable autosave every interval edits."""
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0
    return

def disable_autosave(doc_name: str):
    """Disable autosave."""
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False
    doc.autosave_interval = 0
    doc.autosave_counter = 0
    return
