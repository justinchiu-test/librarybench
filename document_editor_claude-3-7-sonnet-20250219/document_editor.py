from typing import Dict, List, Optional
import uuid
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from copy import deepcopy


class OperationType(Enum):
    """Types of operations that can be applied to a document."""

    INSERT = "insert"
    DELETE = "delete"
    EDIT = "edit"


@dataclass
class Operation:
    """Represents an operation on a document."""

    type: OperationType
    key: str
    value: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class Conflict:
    """Represents a merge conflict."""

    key: str
    source_value: str
    dest_value: str
    ancestor_value: Optional[str] = None
    resolved: bool = False
    resolved_value: Optional[str] = None


@dataclass
class Commit:
    """Represents a commit in the document version history."""

    id: str
    message: str
    timestamp: float
    parent_ids: List[str]
    content: Dict[str, str]
    label: Optional[str] = None


@dataclass
class Document:
    """Represents a document with version control capabilities."""

    name: str
    content: Dict[str, str] = field(default_factory=dict)
    commits: List[Commit] = field(default_factory=list)
    branches: Dict[str, str] = field(default_factory=dict)
    current_branch: str = "main"
    current_commit_id: Optional[str] = None
    has_uncommitted_changes: bool = False
    operation_queue: List[Operation] = field(default_factory=list)
    conflicts: Dict[str, Conflict] = field(default_factory=dict)
    snapshots: Dict[str, str] = field(default_factory=dict)
    autosave_interval: int = 5  # Number of operations before autosave
    autosave_counter: int = 0
    autosave_enabled: bool = False
    autosave_thread: Optional[threading.Thread] = None


# In-memory storage for documents
_documents: Dict[str, Document] = {}


def create_document(name: str) -> Document:
    """Create a new blank document.

    Args:
        name: The name of the document

    Returns:
        The newly created document
    """
    document = Document(name=name)
    document.branches["main"] = None  # No commits yet
    _documents[name] = document
    return document


def edit(doc: str, key: str, value: str) -> None:
    """Update content under the specified key.

    Args:
        doc: The document name
        key: The section ID/key to update
        value: The new content for the section
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    document.content[key] = value
    document.has_uncommitted_changes = True

    # Increment autosave counter
    if document.autosave_enabled:
        document.autosave_counter += 1
        if document.autosave_counter >= document.autosave_interval:
            commit(doc, f"Autosave at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            document.autosave_counter = 0


def apply_operation(doc: str, op: Dict) -> None:
    """Queue an operation for later application.

    Args:
        doc: The document name
        op: The operation to apply (dict with 'type', 'key', and optionally 'value')
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    op_type = op.get("type")
    key = op.get("key")

    if not op_type or not key:
        raise ValueError("Operation must include 'type' and 'key'")

    try:
        operation_type = OperationType(op_type)
    except ValueError:
        raise ValueError(f"Invalid operation type: {op_type}")

    value = op.get("value")
    if operation_type in [OperationType.INSERT, OperationType.EDIT] and value is None:
        raise ValueError(f"Operation type {operation_type.value} requires a 'value'")

    operation = Operation(type=operation_type, key=key, value=value)
    document.operation_queue.append(operation)

    # Increment autosave counter
    if document.autosave_enabled:
        document.autosave_counter += 1
        if document.autosave_counter >= document.autosave_interval:
            sync(doc)
            commit(doc, f"Autosave at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            document.autosave_counter = 0


def sync(doc: str) -> None:
    """Apply all queued operations.

    Args:
        doc: The document name
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    if not document.operation_queue:
        return

    # Sort operations by timestamp to ensure order
    operations = sorted(document.operation_queue, key=lambda op: op.timestamp)

    # Apply operations
    for operation in operations:
        if (
            operation.type == OperationType.INSERT
            or operation.type == OperationType.EDIT
        ):
            document.content[operation.key] = operation.value
            document.has_uncommitted_changes = True
        elif operation.type == OperationType.DELETE:
            if operation.key in document.content:
                del document.content[operation.key]
                document.has_uncommitted_changes = True

    # Clear the queue
    document.operation_queue.clear()


def commit(doc: str, message: str) -> str:
    """Commit current state with a message.

    Args:
        doc: The document name
        message: The commit message

    Returns:
        The ID of the new commit
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    # Apply any pending operations before committing
    if document.operation_queue:
        sync(doc)

    commit_id = str(uuid.uuid4())

    # Determine parent commits
    parent_ids = []
    if document.current_commit_id:
        parent_ids.append(document.current_commit_id)

    # Create new commit with a snapshot of the current content
    new_commit = Commit(
        id=commit_id,
        message=message,
        timestamp=time.time(),
        parent_ids=parent_ids,
        content=deepcopy(document.content),
    )

    document.commits.append(new_commit)
    document.current_commit_id = commit_id
    document.branches[document.current_branch] = commit_id
    document.has_uncommitted_changes = False

    return commit_id


def snapshot(doc: str, label: str) -> str:
    """Tag a specific version with a human-readable label.

    Args:
        doc: The document name
        label: The human-readable label

    Returns:
        The commit ID that was labeled
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    if not document.current_commit_id:
        raise ValueError("Cannot create a snapshot without a commit")

    if label in document.snapshots:
        raise ValueError(f"Snapshot label '{label}' already exists")

    # Find the current commit and add the label
    for commit in document.commits:
        if commit.id == document.current_commit_id:
            commit.label = label
            break

    # Store the mapping from label to commit ID
    document.snapshots[label] = document.current_commit_id

    return document.current_commit_id


def log(doc: str) -> List[Commit]:
    """Return commit history.

    Args:
        doc: The document name

    Returns:
        List of commits in reverse chronological order
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    # Return commits in reverse chronological order
    return list(reversed(document.commits))


def checkout(doc: str, commit_id_or_label: str) -> None:
    """Revert to a previous commit by ID or label.

    Args:
        doc: The document name
        commit_id_or_label: The ID or label of the commit to revert to
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    # Check if it's a label
    commit_id = document.snapshots.get(commit_id_or_label, commit_id_or_label)

    # Find the commit
    target_commit = None
    for commit in document.commits:
        if commit.id == commit_id:
            target_commit = commit
            break

    if not target_commit:
        raise ValueError(f"Commit '{commit_id}' not found")

    # Update document state to match the commit
    document.content = deepcopy(target_commit.content)
    document.current_commit_id = commit_id

    # Update current branch if this commit is the head of a branch
    for branch_name, branch_commit_id in document.branches.items():
        if branch_commit_id == commit_id:
            document.current_branch = branch_name
            break

    document.has_uncommitted_changes = False

    # Clear any conflicts that might exist
    document.conflicts.clear()


def branch(doc: str, branch_name: str) -> None:
    """Fork current state into a new branch.

    Args:
        doc: The document name
        branch_name: The name of the new branch
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    if branch_name in document.branches:
        raise ValueError(f"Branch '{branch_name}' already exists")

    # Create new branch pointing to the current commit
    document.branches[branch_name] = document.current_commit_id
    document.current_branch = branch_name


def _find_common_ancestor(
    document: Document, commit1_id: str, commit2_id: str
) -> Optional[str]:
    """Find the closest common ancestor of two commits.

    This is a simplified implementation that works for basic cases.
    For complex histories, a more sophisticated algorithm would be needed.

    Args:
        document: The document
        commit1_id: First commit ID
        commit2_id: Second commit ID

    Returns:
        The ID of the common ancestor commit, or None if not found
    """
    # Build ancestry paths for both commits
    ancestors1 = set()
    current = commit1_id

    while current:
        ancestors1.add(current)
        # Find commit object
        commit = next((c for c in document.commits if c.id == current), None)
        if not commit or not commit.parent_ids:
            break
        current = commit.parent_ids[
            0
        ]  # For simplicity, we only follow the first parent

    # Check if commit2 or any of its ancestors are in ancestors1
    current = commit2_id
    while current:
        if current in ancestors1:
            return current
        # Find commit object
        commit = next((c for c in document.commits if c.id == current), None)
        if not commit or not commit.parent_ids:
            break
        current = commit.parent_ids[
            0
        ]  # For simplicity, we only follow the first parent

    return None


def _get_commit_by_id(document: Document, commit_id: str) -> Optional[Commit]:
    """Helper function to get a commit by ID."""
    return next((c for c in document.commits if c.id == commit_id), None)


def merge(doc: str, source_branch: str, dest_branch: str) -> str:
    """Merge source branch into destination branch with conflict detection.

    Args:
        doc: The document name
        source_branch: The name of the source branch
        dest_branch: The name of the destination branch

    Returns:
        The ID of the merge commit
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    if source_branch not in document.branches:
        raise ValueError(f"Source branch '{source_branch}' not found")

    if dest_branch not in document.branches:
        raise ValueError(f"Destination branch '{dest_branch}' not found")

    source_commit_id = document.branches[source_branch]
    dest_commit_id = document.branches[dest_branch]

    if not source_commit_id or not dest_commit_id:
        raise ValueError("Cannot merge from or into a branch with no commits")

    # Find source and destination commits
    source_commit = _get_commit_by_id(document, source_commit_id)
    dest_commit = _get_commit_by_id(document, dest_commit_id)

    if not source_commit or not dest_commit:
        raise ValueError("Source or destination commit not found")

    # Find common ancestor
    ancestor_id = _find_common_ancestor(document, source_commit_id, dest_commit_id)
    ancestor_commit = _get_commit_by_id(document, ancestor_id) if ancestor_id else None

    # Checkout the destination branch
    checkout(doc, dest_commit_id)

    # Clear any existing conflicts
    document.conflicts.clear()

    # Perform merge with conflict detection
    for key, value in source_commit.content.items():
        # If key exists in both branches and was modified since ancestor
        if key in dest_commit.content:
            if ancestor_commit and key in ancestor_commit.content:
                # Both branches modified the key since ancestor
                if (
                    source_commit.content[key] != ancestor_commit.content[key]
                    and dest_commit.content[key] != ancestor_commit.content[key]
                    and source_commit.content[key] != dest_commit.content[key]
                ):
                    # Create conflict
                    conflict = Conflict(
                        key=key,
                        source_value=source_commit.content[key],
                        dest_value=dest_commit.content[key],
                        ancestor_value=ancestor_commit.content[key],
                    )
                    document.conflicts[key] = conflict
                    # Use dest value for now (will be resolved later)
                    document.content[key] = dest_commit.content[key]
                else:
                    # No conflict, take the changed value
                    if source_commit.content[key] != ancestor_commit.content[key]:
                        document.content[key] = source_commit.content[key]
            else:
                # No common ancestor, but key exists in both - potential conflict
                if source_commit.content[key] != dest_commit.content[key]:
                    conflict = Conflict(
                        key=key,
                        source_value=source_commit.content[key],
                        dest_value=dest_commit.content[key],
                    )
                    document.conflicts[key] = conflict
                    # Use dest value for now
                    document.content[key] = dest_commit.content[key]
        else:
            # Key only exists in source, add it
            document.content[key] = value

    # Create a merge commit with both parents
    merge_commit_id = str(uuid.uuid4())
    merge_commit = Commit(
        id=merge_commit_id,
        message=f"Merge branch '{source_branch}' into '{dest_branch}'",
        timestamp=time.time(),
        parent_ids=[dest_commit_id, source_commit_id],
        content=deepcopy(document.content),
    )

    document.commits.append(merge_commit)
    document.current_commit_id = merge_commit_id
    document.branches[dest_branch] = merge_commit_id
    document.current_branch = dest_branch

    return merge_commit_id


def resolve_conflict(doc: str, key: str, resolved_value: str) -> None:
    """Resolve a merge conflict for a specific key.

    Args:
        doc: The document name
        key: The key with a conflict
        resolved_value: The value to use for resolution
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    if key not in document.conflicts:
        raise ValueError(f"No conflict found for key '{key}'")

    # Update the conflict as resolved
    conflict = document.conflicts[key]
    conflict.resolved = True
    conflict.resolved_value = resolved_value

    # Update the document content
    document.content[key] = resolved_value
    document.has_uncommitted_changes = True

    # Remove the conflict
    del document.conflicts[key]


def get_conflicts(doc: str) -> Dict[str, Conflict]:
    """Get all unresolved conflicts in the document.

    Args:
        doc: The document name

    Returns:
        Dictionary of unresolved conflicts
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    return document.conflicts


def enable_autosave(doc: str, interval: int = 5) -> None:
    """Enable automatic saving after a number of operations.

    Args:
        doc: The document name
        interval: Number of operations before autosave
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    document.autosave_enabled = True
    document.autosave_interval = interval
    document.autosave_counter = 0


def disable_autosave(doc: str) -> None:
    """Disable automatic saving.

    Args:
        doc: The document name
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")

    document.autosave_enabled = False
