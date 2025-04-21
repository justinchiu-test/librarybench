"""
Document Editor Module

This module provides functionality for creating, editing, and managing versioned documents
with support for branching, merging, and conflict resolution.
"""

import time
import uuid
import threading
from enum import Enum
from copy import deepcopy
from typing import Dict, List, Optional, Set, Tuple, Union, Any

# Global storage of documents
_documents: Dict[str, 'Document'] = {}


class OperationType(Enum):
    """Types of operations that can be performed on a document."""
    INSERT = "insert"
    EDIT = "edit"
    DELETE = "delete"


class Operation:
    """Represents a single operation on a document."""
    
    def __init__(self, type: OperationType, key: str, value: Optional[str] = None, timestamp: Optional[float] = None):
        """
        Initialize an operation.
        
        Args:
            type: The type of operation (insert, edit, delete)
            key: The key in the document to operate on
            value: The value to set (for insert/edit operations)
            timestamp: When the operation occurred (defaults to current time)
        """
        self.type = type
        self.key = key
        self.value = value
        self.timestamp = timestamp if timestamp is not None else time.time()


class Conflict:
    """Represents a merge conflict between two versions."""
    
    def __init__(self, source_value: Optional[str], dest_value: Optional[str]):
        """
        Initialize a conflict.
        
        Args:
            source_value: The value from the source branch
            dest_value: The value from the destination branch
        """
        self.source_value = source_value
        self.dest_value = dest_value


class Commit:
    """Represents a commit in the document history."""
    
    def __init__(self, id: str, message: str, content_snapshot: Dict[str, str], parent_ids: List[str]):
        """
        Initialize a commit.
        
        Args:
            id: Unique identifier for the commit
            message: Commit message
            content_snapshot: Snapshot of document content at commit time
            parent_ids: List of parent commit IDs
        """
        self.id = id
        self.message = message
        self.content_snapshot = content_snapshot
        self.parent_ids = parent_ids


class Document:
    """Represents a versioned document with branching and merging capabilities."""
    
    def __init__(self, name: str):
        """
        Initialize a document.
        
        Args:
            name: The name of the document
        """
        self.name = name
        self.content: Dict[str, str] = {}  # current working content
        self.commits: List[Commit] = []  # list of Commit objects
        self.commit_map: Dict[str, Commit] = {}  # id -> Commit
        self.branches: Dict[str, Optional[str]] = {"main": None}  # branch name -> head commit id
        self.current_branch = "main"
        self.current_commit_id: Optional[str] = None
        self.operation_queue: List[Operation] = []
        self.has_uncommitted_changes = False
        self.snapshots: Dict[str, str] = {}  # label -> commit id
        self.autosave_enabled = False
        self.autosave_interval = 0
        self.autosave_counter = 0
        self.conflicts: Dict[str, Conflict] = {}  # key -> Conflict


def _get_doc(doc_name: str) -> Document:
    """
    Get a document by name.
    
    Args:
        doc_name: The name of the document to retrieve
        
    Returns:
        The document object
        
    Raises:
        ValueError: If the document doesn't exist
    """
    if doc_name not in _documents:
        raise ValueError(f"Document '{doc_name}' does not exist")
    return _documents[doc_name]


def create_document(name: str) -> Document:
    """
    Create a new document.
    
    Args:
        name: The name of the document
        
    Returns:
        The newly created document
    """
    doc = Document(name)
    _documents[name] = doc
    return doc


def edit(doc_name: str, key: str, value: str) -> None:
    """
    Edit a document by setting a key to a value.
    
    Args:
        doc_name: The name of the document
        key: The key to edit
        value: The value to set
    """
    doc = _get_doc(doc_name)
    doc.content[key] = value
    doc.has_uncommitted_changes = True
    
    _handle_autosave(doc)


def _handle_autosave(doc: Document) -> None:
    """
    Handle autosave logic after an edit.
    
    Args:
        doc: The document to check for autosave
    """
    if doc.autosave_enabled:
        doc.autosave_counter += 1
        if doc.autosave_counter >= doc.autosave_interval:
            commit(doc.name, "Autosave")


def _sync(doc: Document) -> None:
    """
    Apply all queued operations to the document.
    
    Args:
        doc: The document to sync
    """
    if not doc.operation_queue:
        return
        
    # Sort operations by timestamp
    ops = sorted(doc.operation_queue, key=lambda o: o.timestamp)
    
    for op in ops:
        if op.type in (OperationType.INSERT, OperationType.EDIT):
            doc.content[op.key] = op.value
        elif op.type == OperationType.DELETE:
            if op.key in doc.content:
                del doc.content[op.key]
                
    doc.operation_queue.clear()
    doc.has_uncommitted_changes = True


def apply_operation(doc_name: str, operation_dict: Dict[str, Any]) -> None:
    """
    Queue an operation to be applied to a document.
    
    Args:
        doc_name: The name of the document
        operation_dict: Dictionary containing operation details
    """
    doc = _get_doc(doc_name)
    
    # Convert string type to enum if needed
    typ = operation_dict.get("type")
    if isinstance(typ, str):
        typ = OperationType(typ)
        
    op = Operation(
        type=typ,
        key=operation_dict.get("key"),
        value=operation_dict.get("value"),
        timestamp=operation_dict.get("timestamp"),
    )
    
    doc.operation_queue.append(op)


def sync(doc_name: str) -> None:
    """
    Apply all queued operations to the document.
    
    Args:
        doc_name: The name of the document
    """
    doc = _get_doc(doc_name)
    _sync(doc)


def enable_autosave(doc_name: str, interval: int) -> None:
    """
    Enable autosave for a document.
    
    Args:
        doc_name: The name of the document
        interval: Number of edits before autosaving
    """
    doc = _get_doc(doc_name)
    doc.autosave_enabled = True
    doc.autosave_interval = interval
    doc.autosave_counter = 0


def disable_autosave(doc_name: str) -> None:
    """
    Disable autosave for a document.
    
    Args:
        doc_name: The name of the document
    """
    doc = _get_doc(doc_name)
    doc.autosave_enabled = False


def snapshot(doc_name: str, label: str) -> Optional[str]:
    """
    Create a named snapshot of the current commit.
    
    Args:
        doc_name: The name of the document
        label: The label for the snapshot
        
    Returns:
        The commit ID of the snapshot, or None if no current commit
    """
    doc = _get_doc(doc_name)
    if doc.current_commit_id is None:
        return None
        
    doc.snapshots[label] = doc.current_commit_id
    return doc.current_commit_id


def log(doc_name: str) -> List[Commit]:
    """
    Get the commit history of a document.
    
    Args:
        doc_name: The name of the document
        
    Returns:
        List of commits in reverse chronological order
    """
    doc = _get_doc(doc_name)
    return list(reversed(doc.commits))


def checkout(doc_name: str, commit_id_or_label: str) -> None:
    """
    Checkout a specific commit or snapshot.
    
    Args:
        doc_name: The name of the document
        commit_id_or_label: Commit ID or snapshot label to checkout
        
    Raises:
        ValueError: If the commit is not found
    """
    doc = _get_doc(doc_name)
    
    # Resolve label to commit ID if needed
    cid = commit_id_or_label
    if cid in doc.snapshots:
        cid = doc.snapshots[cid]
        
    if cid not in doc.commit_map:
        raise ValueError(f"Commit '{cid}' not found")
        
    commit_obj = doc.commit_map[cid]
    
    # Revert content to the commit's snapshot
    doc.content = deepcopy(commit_obj.content_snapshot)
    doc.current_commit_id = cid
    doc.has_uncommitted_changes = False
    doc.operation_queue.clear()
    
    # Update current branch if this commit is a branch head
    for branch_name, head_commit_id in doc.branches.items():
        if head_commit_id == cid:
            doc.current_branch = branch_name
            break


def branch(doc_name: str, branch_name: str) -> None:
    """
    Create a new branch at the current commit.
    
    Args:
        doc_name: The name of the document
        branch_name: The name of the new branch
    """
    doc = _get_doc(doc_name)
    doc.branches[branch_name] = doc.current_commit_id
    doc.current_branch = branch_name


def _get_ancestors(doc: Document, commit_id: Optional[str]) -> Set[str]:
    """
    Get all ancestors of a commit.
    
    Args:
        doc: The document
        commit_id: The commit ID to find ancestors for
        
    Returns:
        Set of ancestor commit IDs
    """
    ancestors = set()
    if commit_id is None:
        return ancestors
        
    stack = [commit_id]
    while stack:
        cid = stack.pop()
        if cid is None or cid in ancestors:
            continue
            
        ancestors.add(cid)
        commit_obj = doc.commit_map.get(cid)
        if commit_obj:
            stack.extend(commit_obj.parent_ids)
            
    return ancestors


def _find_nearest_common_ancestor(doc: Document, src_ancestors: Set[str], dest_ancestors: Set[str]) -> Optional[str]:
    """
    Find the nearest common ancestor between two sets of ancestors.
    
    Args:
        doc: The document
        src_ancestors: Set of source branch ancestors
        dest_ancestors: Set of destination branch ancestors
        
    Returns:
        The nearest common ancestor commit ID, or None if none found
    """
    common_ancestors = src_ancestors.intersection(dest_ancestors)
    
    # Find the most recent common ancestor by checking commits in reverse order
    for commit in doc.commits:
        if commit.id in common_ancestors:
            return commit.id
            
    return None


def _merge_content(
    anc_content: Dict[str, str],
    src_content: Dict[str, str],
    dest_content: Dict[str, str],
    doc: Document
) -> Dict[str, str]:
    """
    Merge content from source and destination branches.
    
    Args:
        anc_content: Content from common ancestor
        src_content: Content from source branch
        dest_content: Content from destination branch
        doc: The document (for storing conflicts)
        
    Returns:
        The merged content
    """
    merged = deepcopy(dest_content)
    doc.conflicts.clear()
    
    # Get all keys from all three snapshots
    all_keys = set(anc_content.keys()) | set(src_content.keys()) | set(dest_content.keys())
    
    for key in all_keys:
        anc_value = anc_content.get(key)
        src_value = src_content.get(key)
        dest_value = dest_content.get(key)
        
        # Determine the merged value based on the three-way merge rules
        if src_value == dest_value:
            # Both branches have the same value
            merged_value = dest_value
        elif src_value == anc_value and dest_value != anc_value:
            # Only destination changed
            merged_value = dest_value
        elif dest_value == anc_value and src_value != anc_value:
            # Only source changed
            merged_value = src_value
        else:
            # Conflict: both branches changed the same key differently
            doc.conflicts[key] = Conflict(src_value, dest_value)
            merged_value = dest_value  # Default to destination value until resolved
        
        # Update the merged content
        if merged_value is None:
            if key in merged:
                del merged[key]
        else:
            merged[key] = merged_value
            
    return merged


def merge(doc_name: str, source_branch: str, dest_branch: str) -> str:
    """
    Merge a source branch into a destination branch.
    
    Args:
        doc_name: The name of the document
        source_branch: The name of the source branch
        dest_branch: The name of the destination branch
        
    Returns:
        The ID of the merge commit
        
    Raises:
        ValueError: If either branch doesn't exist
    """
    doc = _get_doc(doc_name)
    
    if source_branch not in doc.branches or dest_branch not in doc.branches:
        raise ValueError("Branch not found")
        
    src_commit_id = doc.branches[source_branch]
    dest_commit_id = doc.branches[dest_branch]
    
    # Find common ancestor
    src_ancestors = _get_ancestors(doc, src_commit_id)
    dest_ancestors = _get_ancestors(doc, dest_commit_id)
    ancestor_id = _find_nearest_common_ancestor(doc, src_ancestors, dest_ancestors)
    
    # Get content snapshots
    anc_content = {}
    if ancestor_id:
        anc_content = doc.commit_map[ancestor_id].content_snapshot
        
    src_content = {}
    if src_commit_id:
        src_content = doc.commit_map[src_commit_id].content_snapshot
        
    dest_content = {}
    if dest_commit_id:
        dest_content = doc.commit_map[dest_commit_id].content_snapshot
    
    # Perform three-way merge
    merged_content = _merge_content(anc_content, src_content, dest_content, doc)
    
    # Apply merged content
    doc.content = merged_content
    doc.has_uncommitted_changes = True
    
    # Create merge commit
    merge_msg = f"Merge {source_branch} into {dest_branch}"
    parent_ids = [p for p in [dest_commit_id, src_commit_id] if p is not None]
    new_commit_id = _commit_internal(doc, merge_msg, parent_ids)
    
    # Update branch pointers
    doc.branches[dest_branch] = new_commit_id
    doc.current_branch = dest_branch
    doc.current_commit_id = new_commit_id
    
    return new_commit_id


def _commit_internal(doc: Document, message: str, parent_ids: List[str]) -> str:
    """
    Create a new commit object and add it to the document history.
    
    Args:
        doc: The document
        message: The commit message
        parent_ids: List of parent commit IDs
        
    Returns:
        The ID of the new commit
    """
    # Create a snapshot of the current content
    content_snapshot = deepcopy(doc.content)
    
    # Generate a unique commit ID
    commit_id = uuid.uuid4().hex
    
    # Create and store the commit
    commit_obj = Commit(commit_id, message, content_snapshot, parent_ids)
    doc.commits.append(commit_obj)
    doc.commit_map[commit_id] = commit_obj
    
    return commit_id


def commit(doc_name: str, message: str) -> str:
    """
    Commit changes to a document.
    
    Args:
        doc_name: The name of the document
        message: The commit message
        
    Returns:
        The ID of the new commit
    """
    doc = _get_doc(doc_name)
    
    # Apply any queued operations first
    _sync(doc)
    
    # Determine parent commits
    head_commit_id = doc.branches.get(doc.current_branch)
    parent_ids = [head_commit_id] if head_commit_id else []
    
    # Create the commit
    commit_id = _commit_internal(doc, message, parent_ids)
    
    # Update branch head and current commit
    doc.branches[doc.current_branch] = commit_id
    doc.current_commit_id = commit_id
    doc.has_uncommitted_changes = False
    
    # Reset autosave counter
    doc.autosave_counter = 0
    
    return commit_id


def get_conflicts(doc_name: str) -> Dict[str, Conflict]:
    """
    Get all current merge conflicts.
    
    Args:
        doc_name: The name of the document
        
    Returns:
        Dictionary of conflicts (key -> Conflict)
    """
    doc = _get_doc(doc_name)
    return doc.conflicts


def resolve_conflict(doc_name: str, key: str, resolved_value: str) -> None:
    """
    Resolve a merge conflict.
    
    Args:
        doc_name: The name of the document
        key: The key with the conflict
        resolved_value: The value to use for resolution
    """
    doc = _get_doc(doc_name)
    
    if key in doc.conflicts:
        doc.content[key] = resolved_value
        del doc.conflicts[key]
        doc.has_uncommitted_changes = True
