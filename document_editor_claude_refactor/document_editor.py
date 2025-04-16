from typing import Dict, List, Optional, Tuple
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


def _get_document(doc: str) -> Document:
    """Retrieve document by name or raise error if not found.

    Args:
        doc: The document name

    Returns:
        The document

    Raises:
        ValueError: If document not found
    """
    document = _documents.get(doc)
    if not document:
        raise ValueError(f"Document '{doc}' not found")
    return document


def _generate_commit_id() -> str:
    """Generate a new unique commit ID.

    Returns:
        A unique commit ID
    """
    return str(uuid.uuid4())


def _create_commit(
    document: Document, message: str, parent_ids: List[str]
) -> Tuple[str, Commit]:
    """Create a new commit object.

    Args:
        document: The document
        message: The commit message
        parent_ids: List of parent commit IDs

    Returns:
        Tuple of (commit_id, commit_object)
    """
    commit_id = _generate_commit_id()
    new_commit = Commit(
        id=commit_id,
        message=message,
        timestamp=time.time(),
        parent_ids=parent_ids,
        content=deepcopy(document.content),
    )
    return commit_id, new_commit


def _handle_autosave(document: Document, doc_name: str) -> None:
    """Handle autosave logic after an operation.

    Args:
        document: The document
        doc_name: The document name
    """
    if document.autosave_enabled:
        document.autosave_counter += 1
        if document.autosave_counter >= document.autosave_interval:
            # For apply_operation
            if document.operation_queue:
                sync(doc_name)
            commit(doc_name, f"Autosave at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            document.autosave_counter = 0


def _get_commit_by_id(document: Document, commit_id: str) -> Optional[Commit]:
    """Get a commit by ID.

    Args:
        document: The document
        commit_id: The commit ID

    Returns:
        The commit object or None if not found
    """
    return next((c for c in document.commits if c.id == commit_id), None)


def create_document(name: str) -> Document:
    """Create a new blank document.

    Args:
        name: The name of the document

    Returns:
        The newly created document
    """
    document = Document(name=name)
    document.branches["main"] = ""  # No commits yet, using empty string instead of None
    _documents[name] = document
    return document


def edit(doc: str, key: str, value: str) -> None:
    """Update content under the specified key.

    Args:
        doc: The document name
        key: The section ID/key to update
        value: The new content for the section
    """
    document = _get_document(doc)
    document.content[key] = value
    document.has_uncommitted_changes = True
    _handle_autosave(document, doc)


def apply_operation(doc: str, op: Dict) -> None:
    """Queue an operation for later application.

    Args:
        doc: The document name
        op: The operation to apply (dict with 'type', 'key', and optionally 'value')
    """
    document = _get_document(doc)
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
    _handle_autosave(document, doc)


def _apply_single_operation(document: Document, operation: Operation) -> None:
    """Apply a single operation to a document.

    Args:
        document: The document
        operation: The operation to apply
    """
    if operation.type in [OperationType.INSERT, OperationType.EDIT]:
        if operation.value is not None:  # Ensure value is not None before assignment
            document.content[operation.key] = operation.value
            document.has_uncommitted_changes = True
    elif operation.type == OperationType.DELETE:
        if operation.key in document.content:
            del document.content[operation.key]
            document.has_uncommitted_changes = True


def sync(doc: str) -> None:
    """Apply all queued operations.

    Args:
        doc: The document name
    """
    document = _get_document(doc)
    if not document.operation_queue:
        return

    # Sort operations by timestamp to ensure order
    operations = sorted(document.operation_queue, key=lambda op: op.timestamp)

    # Apply operations
    for operation in operations:
        _apply_single_operation(document, operation)

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
    document = _get_document(doc)

    # Apply any pending operations before committing
    if document.operation_queue:
        sync(doc)

    # Determine parent commits
    parent_ids = []
    if document.current_commit_id:
        parent_ids.append(document.current_commit_id)

    # Create new commit
    commit_id, new_commit = _create_commit(document, message, parent_ids)
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
    document = _get_document(doc)

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
    document = _get_document(doc)
    # Return commits in reverse chronological order
    return list(reversed(document.commits))


def checkout(doc: str, commit_id_or_label: str) -> None:
    """Revert to a previous commit by ID or label.

    Args:
        doc: The document name
        commit_id_or_label: The ID or label of the commit to revert to
    """
    document = _get_document(doc)

    # Check if it's a label
    commit_id = document.snapshots.get(commit_id_or_label, commit_id_or_label)

    # Find the commit
    target_commit = _get_commit_by_id(document, commit_id)
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
    document = _get_document(doc)

    if branch_name in document.branches:
        raise ValueError(f"Branch '{branch_name}' already exists")

    # Create new branch pointing to the current commit
    document.branches[branch_name] = (
        document.current_commit_id if document.current_commit_id is not None else ""
    )
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
        commit = _get_commit_by_id(document, current)
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
        commit = _get_commit_by_id(document, current)
        if not commit or not commit.parent_ids:
            break
        current = commit.parent_ids[
            0
        ]  # For simplicity, we only follow the first parent

    return None


def _create_conflict(
    key: str, source_value: str, dest_value: str, ancestor_value: Optional[str] = None
) -> Conflict:
    """Create a conflict object.

    Args:
        key: The key with a conflict
        source_value: The value from the source branch
        dest_value: The value from the destination branch
        ancestor_value: The value from the common ancestor, if any

    Returns:
        A Conflict object
    """
    return Conflict(
        key=key,
        source_value=source_value,
        dest_value=dest_value,
        ancestor_value=ancestor_value,
    )


def _detect_and_handle_conflicts(
    document: Document,
    key: str,
    source_value: str,
    dest_value: str,
    ancestor_commit: Optional[Commit],
) -> None:
    """Detect and handle conflicts during merge.

    Args:
        document: The document
        key: The content key
        source_value: Value from source branch
        dest_value: Value from destination branch
        ancestor_commit: Common ancestor commit, if any
    """
    # If key exists in both branches and was modified since ancestor
    if ancestor_commit and key in ancestor_commit.content:
        # Both branches modified the key since ancestor
        if (
            source_value != ancestor_commit.content[key]
            and dest_value != ancestor_commit.content[key]
            and source_value != dest_value
        ):
            # Create conflict
            conflict = _create_conflict(
                key=key,
                source_value=source_value,
                dest_value=dest_value,
                ancestor_value=ancestor_commit.content[key],
            )
            document.conflicts[key] = conflict
            # Use dest value for now (will be resolved later)
            document.content[key] = dest_value
        else:
            # No conflict, take the changed value
            if source_value != ancestor_commit.content[key]:
                document.content[key] = source_value
    else:
        # No common ancestor, but key exists in both - potential conflict
        if source_value != dest_value:
            conflict = _create_conflict(
                key=key,
                source_value=source_value,
                dest_value=dest_value,
            )
            document.conflicts[key] = conflict
            # Use dest value for now
            document.content[key] = dest_value


def merge(doc: str, source_branch: str, dest_branch: str) -> str:
    """Merge source branch into destination branch with conflict detection.

    Args:
        doc: The document name
        source_branch: The name of the source branch
        dest_branch: The name of the destination branch

    Returns:
        The ID of the merge commit
    """
    document = _get_document(doc)

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
        # If key exists in both branches
        if key in dest_commit.content:
            _detect_and_handle_conflicts(
                document,
                key,
                source_commit.content[key],
                dest_commit.content[key],
                ancestor_commit,
            )
        else:
            # Key only exists in source, add it
            document.content[key] = value

    # Create a merge commit with both parents
    commit_id, merge_commit = _create_commit(
        document,
        f"Merge branch '{source_branch}' into '{dest_branch}'",
        [dest_commit_id, source_commit_id],
    )

    document.commits.append(merge_commit)
    document.current_commit_id = commit_id
    document.branches[dest_branch] = commit_id
    document.current_branch = dest_branch

    return commit_id


def resolve_conflict(doc: str, key: str, resolved_value: str) -> None:
    """Resolve a merge conflict for a specific key.

    Args:
        doc: The document name
        key: The key with a conflict
        resolved_value: The value to use for resolution
    """
    document = _get_document(doc)

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
    document = _get_document(doc)
    return document.conflicts


def enable_autosave(doc: str, interval: int = 5) -> None:
    """Enable automatic saving after a number of operations.

    Args:
        doc: The document name
        interval: Number of operations before autosave
    """
    document = _get_document(doc)
    document.autosave_enabled = True
    document.autosave_interval = interval
    document.autosave_counter = 0


def disable_autosave(doc: str) -> None:
    """Disable automatic saving.

    Args:
        doc: The document name
    """
    document = _get_document(doc)
    document.autosave_enabled = False
