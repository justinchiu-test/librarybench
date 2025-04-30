import pytest
import copy
from design_manager import Document

def test_unlock_and_edit():
    doc = Document()
    # Manually lock a section
    doc.locked_sections.add("section1")
    assert "section1" in doc.locked_sections
    # Unlock it
    doc.unlock_section("section1")
    assert "section1" not in doc.locked_sections
    # Now edit should work
    doc.edit("section1", "New Content")
    assert doc.content["section1"] == "New Content"
    # Editing a non-locked section also works
    doc.edit("section2", "Content2")
    assert doc.content["section2"] == "Content2"
    # Lock and attempt edit -> should fail
    doc.locked_sections.add("section3")
    with pytest.raises(ValueError):
        doc.edit("section3", "Should fail")

def test_collaborators():
    doc = Document()
    doc.add_collaborator("Alice")
    doc.add_collaborator("Bob")
    lst = doc.collaborator_list()
    assert set(lst) == {"Alice", "Bob"}
    # Removing one
    doc.remove_collaborator("Bob")
    lst2 = doc.collaborator_list()
    assert lst2 == ["Alice"]
    # Removing non-existent collaborator does not error
    doc.remove_collaborator("Charlie")
    assert doc.collaborator_list() == ["Alice"]

def test_history_view_operations():
    doc = Document()
    # Initial history has one 'init'
    hv = doc.history_view()
    assert len(hv) == 1
    assert hv[0]["operation"] == "init"
    # Perform some operations
    doc.unlock_section("sec")
    doc.add_collaborator("X")
    doc.edit("sec", "hello")
    doc.template_support("simple")
    hv2 = doc.history_view()
    ops = [h["operation"] for h in hv2]
    assert ops == ["init", "unlock_section", "add_collaborator", "edit", "template_support"]

def test_apply_operation_no_commit():
    doc = Document()
    doc.edit("a", "1")
    # Define an operation that appends "2" to section "a"
    def op(conf):
        conf["a"] = conf.get("a", "") + "2"
        return conf
    result = doc.apply_operation(op)
    # Original content unchanged
    assert doc.content["a"] == "1"
    # Simulated result shows the change
    assert result["a"] == "12"

def test_resolve_conflict():
    ch1 = {"a": 1, "b": 2}
    ch2 = {"b": 3, "c": 4}
    merged = Document.resolve_conflict(ch1, ch2)
    assert merged == {"a":1, "b":3, "c":4}
    # Original dicts unchanged
    assert ch1 == {"a":1, "b":2}
    assert ch2 == {"b":3, "c":4}

def test_template_support_and_errors():
    doc = Document()
    # Valid template
    doc.template_support("simple")
    # Template 'simple' has header and footer
    assert doc.content["header"] == "Header"
    assert doc.content["footer"] == "Footer"
    # Applying a second template overrides/adds
    doc.template_support("full")
    assert doc.content["body"] == "Body"
    # Invalid template should raise
    with pytest.raises(ValueError):
        doc.template_support("nonexistent")

def test_branch_independence():
    doc = Document()
    doc.edit("sec", "main1")
    # Create a branch copy
    branch_doc = doc.branch("feature")
    # Both start with same content
    assert branch_doc.content == {"sec": "main1"}
    # Edit main
    doc.edit("sec", "main2")
    # Branch remains unchanged
    assert branch_doc.content == {"sec": "main1"}
    # Edit branch
    branch_doc.edit("sec", "feature-change")
    assert branch_doc.content["sec"] == "feature-change"
    assert doc.content["sec"] == "main2"

def test_checkout_and_redo():
    doc = Document()
    # Create some versions
    doc.edit("a", "v1")
    doc.edit("b", "v2")
    doc.edit("c", "v3")
    # History snapshots of content
    snapshots = [h["content"] for h in doc.history]
    # Checkout back to version 1 (after editing 'a')
    doc.checkout(1)
    assert doc.content == snapshots[1]
    # Now redo should restore to version before checkout (which was snapshot[3])
    doc.redo()
    # After redo, content equals the top of redo_history from before
    assert doc.content == snapshots[3]
    # No more redo possible
    with pytest.raises(IndexError):
        doc.redo()
    # Invalid checkout index
    with pytest.raises(IndexError):
        doc.checkout(999)
