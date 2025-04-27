import time
import uuid
import copy
from enum import Enum


# Enum for operation types
class OperationType(Enum):
    INSERT = "insert"
    EDIT = "edit"
    DELETE = "delete"


# Operation class
class Operation:
    def __init__(self, type, key, value=None, timestamp=None):
        self.type = type
        self.key = key
        self.value = value
        self.timestamp = timestamp if timestamp is not None else time.time()


# Conflict representation
class Conflict:
    def __init__(self, source_value, dest_value):
        self.source_value = source_value
        self.dest_value = dest_value


# Commit representation
class Commit:
    def __init__(self, id, message, parents, content_snapshot):
        self.id = id
        self.message = message
        self.parents = parents  # list of parent commit IDs
        # Deep copy snapshot to freeze state
        self.content_snapshot = copy.deepcopy(content_snapshot)


# Document representation
class Document:
    def __init__(self, name):
        self.name = name
        self.content = {}  # key -> value
        self.commits = []  # list of Commit objects in creation order
        self.commit_map = {}  # id -> Commit
        # Branches: name -> commit_id
        self.branches = {"main": None}
        self.current_branch = "main"
        self.current_commit_id = None
        # Operation queue
        self.operation_queue = []
        self.has_uncommitted_changes = False
        # Snapshots by label
        self.snapshots = {}
        # Conflicts after merge
        self.conflicts = {}
        # Autosave
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0


# Global registry of documents by name
docs = {}


# Helper to get document by name
def _get_doc(doc_name):
    if isinstance(doc_name, Document):
        return doc_name
    return docs.get(doc_name)


# Create a new document
def create_document(name: str):
    doc = Document(name)
    docs[name] = doc
    return doc


# Apply a direct edit (bypassing queue)
def edit(doc_name: str, key: str, value: str):
    doc = _get_doc(doc_name)
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    # Autosave logic
    if doc.autosave_enabled:
        doc.autosave_counter += 1
        if doc.autosave_counter >= doc.autosave_interval:
            # Perform autosave commit
            commit(doc_name, "Autosave")
    return None


# Find common ancestor commit ID of two commits
def _find_common_ancestor(doc: Document, id1, id2):
    if id1 is None or id2 is None:
        return None
    # Gather ancestors of id1
    ancestors1 = set()
    stack = [id1]
    while stack:
        cid = stack.pop()
        if cid is None or cid in ancestors1:
            continue
        ancestors1.add(cid)
        commit = doc.commit_map.get(cid)
        if commit:
            for p in commit.parents:
                stack.append(p)
    # BFS ancestors of id2 to find first in ancestors1
    stack = [id2]
    visited = set()
    while stack:
        cid = stack.pop(0)
        if cid is None or cid in visited:
            continue
        visited.add(cid)
        if cid in ancestors1:
            return cid
        commit = doc.commit_map.get(cid)
        if commit:
            for p in commit.parents:
                stack.append(p)
    return None


# Commit current state
def commit(doc_name: str, message: str):
    doc = _get_doc(doc_name)
    # First sync any queued operations
    if doc.operation_queue:
        sync(doc_name)
    # Prepare commit
    parent = doc.current_commit_id
    commit_id = uuid.uuid4().hex
    parents = [parent] if parent is not None else []
    snapshot = copy.deepcopy(doc.content)
    new_commit = Commit(commit_id, message, parents, snapshot)
    # Register commit
    doc.commits.append(new_commit)
    doc.commit_map[commit_id] = new_commit
    # Update branch pointer
    doc.branches[doc.current_branch] = commit_id
    doc.current_commit_id = commit_id
    # Reset uncommitted flag and autosave counter
    doc.has_uncommitted_changes = False
    doc.autosave_counter = 0
    return commit_id


# Return commit history (newest first)
def log(doc_name: str):
    doc = _get_doc(doc_name)
    # Return reversed commits list
    return list(reversed(doc.commits))


# Checkout to a commit ID or snapshot label
def checkout(doc_name: str, commit_id_or_label: str):
    doc = _get_doc(doc_name)
    # Resolve label
    target_id = None
    if commit_id_or_label in doc.snapshots:
        target_id = doc.snapshots[commit_id_or_label]
    else:
        target_id = commit_id_or_label
    # Validate
    if target_id not in doc.commit_map:
        return None
    commit_obj = doc.commit_map[target_id]
    # Restore content
    doc.content = copy.deepcopy(commit_obj.content_snapshot)
    doc.current_commit_id = target_id
    # Clear queued operations
    doc.operation_queue = []
    # Reset uncommitted changes
    doc.has_uncommitted_changes = False
    # Switch branch if matches a branch head
    for bname, bid in doc.branches.items():
        if bid == target_id:
            doc.current_branch = bname
            break
    return None


# Create a new branch from current commit and switch to it
def branch(doc_name: str, branch_name: str):
    doc = _get_doc(doc_name)
    # Point new branch at current commit
    doc.branches[branch_name] = doc.current_commit_id
    doc.current_branch = branch_name
    return None


# Merge source_branch into dest_branch
def merge(doc_name: str, source_branch: str, dest_branch: str):
    doc = _get_doc(doc_name)
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        return None
    src_id = doc.branches[source_branch]
    dest_id = doc.branches[dest_branch]
    # Find common ancestor
    base_id = _find_common_ancestor(doc, src_id, dest_id)
    base_snapshot = {}
    if base_id and base_id in doc.commit_map:
        base_snapshot = doc.commit_map[base_id].content_snapshot
    # Load source and dest snapshots
    src_snapshot = {}
    if src_id:
        src_snapshot = doc.commit_map[src_id].content_snapshot
    dest_snapshot = {}
    if dest_id:
        dest_snapshot = doc.commit_map[dest_id].content_snapshot
    # Switch to dest branch state
    doc.current_branch = dest_branch
    doc.current_commit_id = dest_id
    # Start merge
    merged = copy.deepcopy(dest_snapshot)
    doc.conflicts = {}
    # Collect all keys
    keys = set(base_snapshot.keys()) | set(src_snapshot.keys()) | set(dest_snapshot.keys())
    for key in keys:
        base_v = base_snapshot.get(key)
        src_v = src_snapshot.get(key)
        dest_v = dest_snapshot.get(key)
        # Detect conflict
        if (base_v != src_v) and (base_v != dest_v) and (src_v != dest_v):
            # conflict: keep dest until resolution
            doc.conflicts[key] = Conflict(src_v, dest_v)
            merged_val = dest_v
        else:
            # Non-conflict: if dest same as base and src changed, take src
            if base_v == dest_v and base_v != src_v:
                merged_val = src_v
            else:
                # otherwise keep dest
                merged_val = dest_v
        # Apply merged_val (could be None => deletion)
        if merged_val is None:
            if key in merged:
                del merged[key]
        else:
            merged[key] = merged_val
    # Update document content
    doc.content = merged
    doc.has_uncommitted_changes = True
    # Create merge commit with two parents
    merge_commit_id = uuid.uuid4().hex
    parents = []
    if dest_id:
        parents.append(dest_id)
    if src_id:
        parents.append(src_id)
    merge_snapshot = copy.deepcopy(doc.content)
    merge_commit = Commit(merge_commit_id, f"Merge {source_branch} into {dest_branch}", parents, merge_snapshot)
    # Register merge commit
    doc.commits.append(merge_commit)
    doc.commit_map[merge_commit_id] = merge_commit
    # Update branch head
    doc.branches[dest_branch] = merge_commit_id
    doc.current_commit_id = merge_commit_id
    # After commit, clear uncommitted
    doc.has_uncommitted_changes = False
    return merge_commit_id


# Queue an operation
def apply_operation(doc_name: str, op_dict: dict):
    doc = _get_doc(doc_name)
    typ = op_dict.get("type", "").lower()
    try:
        op_type = OperationType(typ)
    except ValueError:
        # Try mapping by string
        op_type = OperationType(typ)
    key = op_dict.get("key")
    value = op_dict.get("value")
    timestamp = op_dict.get("timestamp", None)
    op = Operation(op_type, key, value, timestamp)
    doc.operation_queue.append(op)
    return None


# Apply queued operations
def sync(doc_name: str):
    doc = _get_doc(doc_name)
    # Sort by timestamp
    doc.operation_queue.sort(key=lambda o: o.timestamp)
    for op in doc.operation_queue:
        if op.type == OperationType.INSERT or op.type == OperationType.EDIT:
            doc.content[op.key] = op.value
        elif op.type == OperationType.DELETE:
            if op.key in doc.content:
                del doc.content[op.key]
    # Clear queue
    doc.operation_queue = []
    doc.has_uncommitted_changes = True
    return None


# Snapshot current commit with label
def snapshot(doc_name: str, label: str):
    doc = _get_doc(doc_name)
    # Label current commit
    doc.snapshots[label] = doc.current_commit_id
    return doc.current_commit_id


# Get current conflicts
def get_conflicts(doc_name: str):
    doc = _get_doc(doc_name)
    return doc.conflicts


# Resolve a conflict
def resolve_conflict(doc_name: str, key: str, resolved_value: str):
    doc = _get_doc(doc_name)
    if key in doc.conflicts:
        # Apply resolution
        doc.content[key] = resolved_value
        # Remove from conflicts
        del doc.conflicts[key]
        doc.has_uncommitted_changes = True
    return None


# Enable autosave
def enable_autosave(doc_name: str, interval: int):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0
    return None


# Disable autosave
def disable_autosave(doc_name: str):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False
    return None
