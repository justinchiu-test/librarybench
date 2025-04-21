# The Task Update

We want some updated functionality. Version 2 includes conflict resolution and real-time operation queing.

# New features to add:

Real-time Operation Queueing

* Add an `apply_operation` function that queues operations (e.g., insert/delete/edit), simulating real-time user edits, and make sure to add operation to flu sh and apply queued operations in order.

Conflict Resolution on Merge

* In `merge`, if the same key is modified in both branches since their common ancestor, mark as a conflict and include both versions.
* Add `resolve_conflict(doc, key, resolved_value)`.

Snapshots

* Add `snapshot(doc, label)` to tag a specific version with a human-readable label.
* Allow `checkout` by label or commit ID.

Autosave / Background Commit

* Add a background process (simulated) that periodically autosaves edits every N operations.

