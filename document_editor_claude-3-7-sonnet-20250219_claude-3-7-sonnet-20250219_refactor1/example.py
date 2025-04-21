from document_editor import (
    create_document,
    edit,
    commit as do_commit,
    log,
    checkout,
    branch,
    merge,
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


def main():
    """Demonstrate document editor functionality."""
    print("Creating a new document 'example_doc'...")
    doc = create_document("example_doc")
    print_document_state("example_doc", doc)

    print("\nEditing document...")
    edit("example_doc", "introduction", "This is the introduction to our document.")
    edit("example_doc", "section1", "This is the content of section 1.")
    print_document_state("example_doc", doc)

    print("\nCommitting changes...")
    commit_id = do_commit("example_doc", "Initial content")
    print(f"Created commit: {commit_id}")
    print_document_state("example_doc", doc)

    print("\nCreating a feature branch...")
    branch("example_doc", "feature")
    print_document_state("example_doc", doc)

    print("\nEditing on feature branch...")
    edit("example_doc", "section2", "This is new content added in the feature branch.")
    edit("example_doc", "section1", "This section was modified in the feature branch.")
    commit_id = do_commit("example_doc", "Feature branch changes")
    print(f"Created commit on feature branch: {commit_id}")
    print_document_state("example_doc", doc)

    print("\nSwitching back to main branch...")
    checkout("example_doc", doc.branches["main"])
    print_document_state("example_doc", doc)

    print("\nEditing on main branch...")
    edit(
        "example_doc", "conclusion", "This is the conclusion added on the main branch."
    )
    commit_id = do_commit("example_doc", "Added conclusion on main")
    print(f"Created commit on main branch: {commit_id}")
    print_document_state("example_doc", doc)

    print("\nMerging feature branch into main...")
    merge_commit = merge("example_doc", "feature", "main")
    print(f"Created merge commit: {merge_commit}")
    print_document_state("example_doc", doc)

    print("\nLog history:")
    history = log("example_doc")
    for i, commit in enumerate(history):
        print(f"{i + 1}. Commit {commit.id[:8]} - {commit.message}")
        print(f"   Parents: {[p_id[:8] for p_id in commit.parent_ids]}")


if __name__ == "__main__":
    main()
