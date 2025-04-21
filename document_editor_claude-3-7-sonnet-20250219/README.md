# Document Editor

A collaborative document editor that supports versioning, branching, merging, conflict resolution, and real-time operation queueing. The document is represented as a key-value store (where keys are paragraphs or section IDs), and provides methods to mutate state while maintaining version history.

## Features

### Core Functionality
- Create and edit documents
- Commit changes with messages
- View commit history
- Checkout previous versions
- Create branches for parallel editing
- Merge changes between branches

### Advanced Features
- Real-time operation queueing (insert/edit/delete operations)
- Conflict detection and resolution
- Named snapshots with human-readable labels
- Autosave functionality

## Installation

Clone this repository and install dependencies:

```bash
git clone <repository-url>
cd document_editor
uv sync
```

## Usage

### Basic Operations

```python
from document_editor import (
    create_document, 
    edit, 
    commit, 
    log, 
    checkout, 
    branch, 
    merge
)

# Create a document
doc = create_document("my_document")

# Edit the document
edit("my_document", "introduction", "This is the introduction.")
edit("my_document", "section1", "This is section 1.")

# Commit changes
commit_id = commit("my_document", "Initial content")

# View history
history = log("my_document")
for commit in history:
    print(f"Commit: {commit.id} - {commit.message}")

# Checkout previous version
checkout("my_document", commit_id)
```

### Branching and Merging

```python
# Create a new branch
branch("my_document", "feature")

# Make changes on the feature branch
edit("my_document", "section2", "New section in feature branch.")
feature_commit = commit("my_document", "Add section in feature branch")

# Switch back to main branch
checkout("my_document", doc.branches["main"])

# Make changes on main branch
edit("my_document", "conclusion", "This is the conclusion.")
main_commit = commit("my_document", "Add conclusion")

# Merge feature branch into main
merge("my_document", "feature", "main")
```

### Real-time Operation Queueing

```python
from document_editor import apply_operation, sync

# Queue operations
apply_operation("my_document", {
    "type": "insert", 
    "key": "section3", 
    "value": "This is section 3."
})

apply_operation("my_document", {
    "type": "edit", 
    "key": "section1", 
    "value": "Updated section 1."
})

apply_operation("my_document", {
    "type": "delete", 
    "key": "section2"
})

# Apply all queued operations
sync("my_document")
```

### Snapshots and Labeled Versions

```python
from document_editor import snapshot

# Create a snapshot with a label
snapshot("my_document", "v1.0")

# Make more changes...
edit("my_document", "section1", "Updated content.")
commit("my_document", "Update content")

# Checkout by label
checkout("my_document", "v1.0")
```

### Conflict Resolution

```python
from document_editor import get_conflicts, resolve_conflict

# After a merge with conflicts...
conflicts = get_conflicts("my_document")

for key, conflict in conflicts.items():
    print(f"Conflict in '{key}':")
    print(f"Source: {conflict.source_value}")
    print(f"Destination: {conflict.dest_value}")
    
    # Resolve the conflict
    resolved_value = "Manually resolved content"
    resolve_conflict("my_document", key, resolved_value)

# Commit the resolved conflicts
commit("my_document", "Resolve conflicts")
```

### Autosave

```python
from document_editor import enable_autosave, disable_autosave

# Enable autosave every 5 operations
enable_autosave("my_document", 5)

# ... make edits ...

# Disable autosave
disable_autosave("my_document")
```

## Examples

Run the example scripts to see the document editor in action:

```bash
# Basic functionality example
uv run python example.py

# Advanced features example (V2)
uv run python example_v2.py
```

## Testing

Run the tests to verify the implementation:

```bash
uv run pytest test.py
```