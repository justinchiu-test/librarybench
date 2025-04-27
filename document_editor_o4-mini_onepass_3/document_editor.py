import time
import uuid
import copy
from enum import Enum, auto

# In-memory store of documents
_documents = {}

class OperationType(Enum):
    INSERT = auto()
    EDIT = auto()
    DELETE = auto()

class Operation:
    def __init__(self, type, key, value=None, timestamp=None):
        self.type = type
        self.key = key
        self.value = value
        self.timestamp = timestamp if timestamp is not None else time.time()

class Commit:
    def __init__(self, id, message, content_snapshot, parents, timestamp=None):
        self.id = id
        self.message = message
        # deep copy snapshot
        self.content = copy.deepcopy(content_snapshot)
        self.parents = parents[:]  # list of parent commit ids
        self.timestamp = timestamp if timestamp is not None else time.time()

class Conflict:
    def __init__(self, source_value, dest_value):
        self.source_value = source_value
        self.dest_value = dest_value

class Document:
    def __init__(self, name):
        self.name = name
        self.content = {}  # current working content
        self.commits = []  # list of Commit objects in creation order
        self.commit_map = {}  # id -> Commit
        self.branches = {'main': None}  # branch name -> commit id
        self.current_branch = 'main'
        self.current_commit_id = None
        self.operation_queue = []
        self.has_uncommitted_changes = False
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0
        self.snapshots = {}  # label -> commit id
        self.conflicts = {}  # key -> Conflict

    def _increment_autosave(self):
        if self.autosave_enabled:
            self.autosave_counter += 1
            if self.autosave_counter >= self.autosave_interval:
                # perform autosave commit
                # reset counter inside commit
                commit(self.name, f"autosave")
    
def create_document(name: str):
    doc = Document(name)
    _documents[name] = doc
    return doc

def _get_doc(name):
    if name not in _documents:
        raise ValueError(f"Document '{name}' does not exist")
    return _documents[name]

def edit(doc_name: str, key: str, value: str):
    doc = _get_doc(doc_name)
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    doc._increment_autosave()

def apply_operation(doc_name: str, op_dict: dict):
    doc = _get_doc(doc_name)
    typ = op_dict.get('type')
    if isinstance(typ, str):
        t = typ.lower()
        if t == 'insert':
            op_type = OperationType.INSERT
        elif t == 'edit':
            op_type = OperationType.EDIT
        elif t == 'delete':
            op_type = OperationType.DELETE
        else:
            raise ValueError("Unknown operation type")
    else:
        op_type = typ
    op = Operation(
        type=op_type,
        key=op_dict.get('key'),
        value=op_dict.get('value'),
        timestamp=op_dict.get('timestamp', None)
    )
    doc.operation_queue.append(op)

def sync(doc_name: str):
    doc = _get_doc(doc_name)
    if not doc.operation_queue:
        return
    # sort by timestamp
    doc.operation_queue.sort(key=lambda o: o.timestamp)
    for op in doc.operation_queue:
        if op.type == OperationType.INSERT or op.type == OperationType.EDIT:
            doc.content[op.key] = op.value
        elif op.type == OperationType.DELETE:
            if op.key in doc.content:
                del doc.content[op.key]
    doc.operation_queue.clear()
    doc.has_uncommitted_changes = True

def commit(doc_name: str, message: str):
    doc = _get_doc(doc_name)
    # first auto-sync operations
    sync(doc_name)
    cid = uuid.uuid4().hex
    parents = []
    if doc.current_commit_id:
        parents.append(doc.current_commit_id)
    snapshot = copy.deepcopy(doc.content)
    new_commit = Commit(cid, message, snapshot, parents)
    doc.commits.append(new_commit)
    doc.commit_map[cid] = new_commit
    # update branch
    doc.current_commit_id = cid
    doc.branches[doc.current_branch] = cid
    # reset flags
    doc.has_uncommitted_changes = False
    doc.autosave_counter = 0
    return cid

def log(doc_name: str):
    doc = _get_doc(doc_name)
    history = []
    cid = doc.current_commit_id
    while cid:
        c = doc.commit_map.get(cid)
        if not c:
            break
        history.append(c)
        # first parent
        if c.parents:
            cid = c.parents[0]
        else:
            break
    return history

def checkout(doc_name: str, commit_or_label: str):
    doc = _get_doc(doc_name)
    # resolve label
    cid = commit_or_label
    if commit_or_label in doc.snapshots:
        cid = doc.snapshots[commit_or_label]
    if cid not in doc.commit_map:
        raise ValueError("Unknown commit/label")
    # set content to snapshot
    snapshot = doc.commit_map[cid].content
    doc.content = copy.deepcopy(snapshot)
    doc.current_commit_id = cid
    # switch branch if this is a branch head
    for b, head in doc.branches.items():
        if head == cid:
            doc.current_branch = b
            break
    doc.has_uncommitted_changes = False

def branch(doc_name: str, branch_name: str):
    doc = _get_doc(doc_name)
    if branch_name in doc.branches:
        raise ValueError("Branch exists")
    # new branch from current commit
    doc.branches[branch_name] = doc.current_commit_id
    doc.current_branch = branch_name

def _collect_ancestors(doc, cid):
    seen = set()
    stack = [cid]
    while stack:
        cur = stack.pop()
        if cur and cur not in seen:
            seen.add(cur)
            c = doc.commit_map.get(cur)
            if c:
                stack.extend(c.parents)
    return seen

def _find_common_ancestor(doc, c1, c2):
    if c1 is None or c2 is None:
        return None
    anc1 = _collect_ancestors(doc, c1)
    # BFS from c2
    queue = [c2]
    visited = set()
    while queue:
        cur = queue.pop(0)
        if cur in anc1:
            return cur
        if cur and cur not in visited:
            visited.add(cur)
            c = doc.commit_map.get(cur)
            if c:
                queue.extend(c.parents)
    return None

def merge(doc_name: str, source_branch: str, dest_branch: str):
    doc = _get_doc(doc_name)
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        raise ValueError("Unknown branch")
    source_cid = doc.branches[source_branch]
    dest_cid = doc.branches[dest_branch]
    # checkout dest branch tip
    doc.current_branch = dest_branch
    checkout(doc_name, dest_cid)
    ancestor_cid = _find_common_ancestor(doc, source_cid, dest_cid)
    ancestor_content = {}
    if ancestor_cid:
        ancestor_content = doc.commit_map[ancestor_cid].content
    source_content = {}
    if source_cid:
        source_content = doc.commit_map[source_cid].content
    # perform merge into doc.content (currently dest snapshot)
    new_content = copy.deepcopy(doc.content)
    for key in set().union(ancestor_content.keys(),
                           source_content.keys(),
                           doc.content.keys()):
        anc = ancestor_content.get(key)
        src = source_content.get(key)
        dst = doc.content.get(key)
        changed_src = (src != anc)
        changed_dst = (dst != anc)
        if changed_src and changed_dst and src != dst:
            # conflict
            doc.conflicts[key] = Conflict(src, dst)
            # keep dest until resolution
            new_content[key] = dst
        elif changed_src:
            # take source
            if src is None:
                if key in new_content:
                    del new_content[key]
            else:
                new_content[key] = src
        else:
            # keep dest
            pass
    doc.content = new_content
    # mark
    doc.has_uncommitted_changes = True
    # commit merge
    merge_msg = f"Merge {source_branch} into {dest_branch}"
    # create commit with two parents
    sync(doc_name)
    mid = uuid.uuid4().hex
    parents = []
    if dest_cid:
        parents.append(dest_cid)
    if source_cid:
        parents.append(source_cid)
    snap = copy.deepcopy(doc.content)
    mcommit = Commit(mid, merge_msg, snap, parents)
    doc.commits.append(mcommit)
    doc.commit_map[mid] = mcommit
    doc.current_commit_id = mid
    doc.branches[dest_branch] = mid
    doc.has_uncommitted_changes = False
    return mid

def snapshot(doc_name: str, label: str):
    doc = _get_doc(doc_name)
    if not doc.current_commit_id:
        raise ValueError("No commit to snapshot")
    doc.snapshots[label] = doc.current_commit_id
    return doc.current_commit_id

def get_conflicts(doc_name: str):
    doc = _get_doc(doc_name)
    return doc.conflicts.copy()

def resolve_conflict(doc_name: str, key: str, resolved_value: str):
    doc = _get_doc(doc_name)
    if key not in doc.conflicts:
        raise ValueError("No such conflict")
    doc.content[key] = resolved_value
    del doc.conflicts[key]
    doc.has_uncommitted_changes = True

def enable_autosave(doc_name: str, interval: int):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0

def disable_autosave(doc_name: str):
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False
    doc.autosave_interval = 0
    doc.autosave_counter = 0
