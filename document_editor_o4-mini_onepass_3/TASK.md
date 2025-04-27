# The Task

Implement a simple collaborative document editor that supports versioning, branching, and merging. Internally, you’ll represent the document as a key-value store (where keys are paragraphs or section IDs), and provide methods to mutate state while maintaining version history.

# Requirements:

* `create_document(name: str)` → create a new blank document
* `edit(doc: str, key: str, value: str)` → update content under key (e.g. section ID)
* `commit(doc: str, message: str)` → commit current state with message
* `log(doc: str) → return commit history
* `checkout(doc: str, commit_id: str)` → revert to a previous commit
* `branch(doc: str, branch_name: str)` → fork current state into a new branch
* `merge(doc: str, source_branch: str, dest_branch: str)` → naive merge

# Data structure highlights:

* DAG of commits
* Namespaced branches
* Snapshotting logic
