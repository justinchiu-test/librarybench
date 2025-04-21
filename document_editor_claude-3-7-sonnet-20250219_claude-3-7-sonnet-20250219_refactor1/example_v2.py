from document_editor import (
    create_document,
    edit,
    commit as do_commit,
    log,
    checkout,
    branch,
    merge,
    apply_operation,
    sync,
    snapshot,
    get_conflicts,
    resolve_conflict,
    enable_autosave,
    disable_autosave,
)


def print_document_state(doc_name, document):
    """Print the current state of the document."""
    print(f"\n=== Document: {doc_name} ===")
    print(f"Current branch: {document.current_branch}")
    print(f"Current commit: {document.current_commit_id}")
    print("Content:")
    if document.content:
        for key, value in document.content.items():
            print(f"  {key}: {value}")
    else:
        print("  (empty)")
    print("=" * 30)


def print_conflicts(conflicts):
    """Print conflict information."""
    if not conflicts:
        print("No conflicts")
        return

    print("\n=== Conflicts ===")
    for key, conflict in conflicts.items():
        print(f"Conflict in '{key}':")
        print(f"  Source value: {conflict.source_value}")
        print(f"  Destination value: {conflict.dest_value}")
        if conflict.ancestor_value:
            print(f"  Ancestor value: {conflict.ancestor_value}")
        print("-" * 20)


def main():
    """Demonstrate document editor functionality."""
    print("Creating a new document 'example_doc'...")
    doc = create_document("example_doc")
    print_document_state("example_doc", doc)

    print("\n=== Part 1: Real-time Operation Queueing ===")
    print("\nAdding operations to queue...")
    apply_operation(
        "example_doc",
        {"type": "insert", "key": "introduction", "value": "This is the introduction."},
    )
    apply_operation(
        "example_doc",
        {"type": "insert", "key": "section1", "value": "This is section 1."},
    )
    print("Operations queued, but not yet applied.")
    print_document_state("example_doc", doc)

    print("\nSyncing operations...")
    sync("example_doc")
    print_document_state("example_doc", doc)

    print("\nCommitting changes...")
    commit_id = do_commit("example_doc", "Initial content")
    print(f"Created commit: {commit_id}")
    print_document_state("example_doc", doc)

    print("\n=== Part 2: Snapshots ===")
    print("\nCreating snapshot 'v1.0'...")
    snapshot_id = snapshot("example_doc", "v1.0")
    print(f"Snapshot created with ID: {snapshot_id}")

    print("\nMaking more changes...")
    edit("example_doc", "introduction", "This is the updated introduction.")
    edit("example_doc", "section2", "This is a new section added after the snapshot.")
    new_commit_id = do_commit("example_doc", "Update content")
    print(f"Created new commit: {new_commit_id}")
    print_document_state("example_doc", doc)

    print("\nChecking out snapshot 'v1.0'...")
    checkout("example_doc", "v1.0")
    print_document_state("example_doc", doc)

    print("\nChecking out latest commit again...")
    checkout("example_doc", new_commit_id)
    print_document_state("example_doc", doc)

    print("\n=== Part 3: Conflict Resolution ===")
    print("\nCreating initial content for conflict demo...")
    doc_name = "conflict_doc"
    conflict_doc = create_document(doc_name)
    edit(doc_name, "shared_section", "Original shared content")
    common_commit = do_commit(doc_name, "Initial content")
    print_document_state(doc_name, conflict_doc)

    print("\nCreating feature branch...")
    branch(doc_name, "feature")
    edit(doc_name, "shared_section", "Feature branch version of shared content")
    do_commit(doc_name, "Feature changes")
    print_document_state(doc_name, conflict_doc)

    print("\nSwitching back to main branch...")
    checkout(doc_name, common_commit)
    edit(doc_name, "shared_section", "Main branch version of shared content")
    do_commit(doc_name, "Main changes")
    print_document_state(doc_name, conflict_doc)

    print("\nMerging feature branch into main (with conflict detection)...")
    merge(doc_name, "feature", "main")
    print_document_state(doc_name, conflict_doc)

    conflicts = get_conflicts(doc_name)
    print_conflicts(conflicts)

    if conflicts:
        print("\nResolving conflict...")
        resolve_conflict(doc_name, "shared_section", "Manually resolved shared content")
        print_document_state(doc_name, conflict_doc)

        print("\nCommitting resolution...")
        resolution_commit = do_commit(doc_name, "Resolve conflict")
        print(f"Created resolution commit: {resolution_commit}")
        print_document_state(doc_name, conflict_doc)

    print("\n=== Part 4: Autosave ===")
    print("\nCreating document with autosave...")
    autosave_doc_name = "autosave_doc"
    autosave_doc = create_document(autosave_doc_name)

    print("\nEnabling autosave every 2 operations...")
    enable_autosave(autosave_doc_name, 2)

    print("\nMaking first edit (shouldn't trigger autosave)...")
    edit(autosave_doc_name, "auto_section1", "Autosave content 1")
    print_document_state(autosave_doc_name, autosave_doc)

    print("\nMaking second edit (should trigger autosave)...")
    edit(autosave_doc_name, "auto_section2", "Autosave content 2")
    print_document_state(autosave_doc_name, autosave_doc)

    print("\nDisabling autosave...")
    disable_autosave(autosave_doc_name)

    print("\nMaking more edits (shouldn't trigger autosave)...")
    edit(autosave_doc_name, "auto_section3", "No autosave content")
    print_document_state(autosave_doc_name, autosave_doc)

    print("\nLog history:")
    history = log(autosave_doc_name)
    for i, entry in enumerate(history):
        print(f"{i + 1}. Commit {entry.id[:8]} - {entry.message}")
        print(f"   Parents: {[p_id[:8] for p_id in entry.parent_ids]}")
        if entry.label:
            print(f"   Label: {entry.label}")


if __name__ == "__main__":
    main()