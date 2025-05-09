import pytest
from doc_manager import Document

def test_basic_edit_and_autosave_and_flush():
    doc = Document()
    # Initially no sections
    assert doc.sections == {}
    # Edit section "Intro"
    doc.edit("Intro", "Welcome to the project.")
    # After edit (with autosave), queued_ops should be empty and section applied
    assert doc.sections["Intro"] == "Welcome to the project."
    # Activity log should include scheduling, flush, autosave
    feed = doc.get_activity_feed()
    assert "Scheduled edit on section 'Intro'" in feed
    # At least one flush and one autosave entry
    assert any("Flushed operations" in e for e in feed)
    assert any("Autosaved document" in e for e in feed)

def test_commit_creates_version_and_activity():
    doc = Document()
    doc.edit("Sec1", "First content")
    v0 = doc.commit("Initial commit")
    assert v0 == 0
    # Version snapshot should be stored
    assert len(doc.versions) == 1
    assert doc.versions[0]["Sec1"] == "First content"
    # Activity feed records commit
    feed = doc.get_activity_feed()
    assert f"Committed version 0: Initial commit" in feed

def test_version_compare_diff():
    doc = Document()
    doc.edit("A", "one")
    v0 = doc.commit("c0")
    doc.edit("A", "two")
    v1 = doc.commit("c1")
    diff = doc.version_compare(v0, v1)
    # Diff should show 'one' replaced by 'two'
    assert "-one" in diff
    assert "+two" in diff
    assert f"v{v0}" in diff and f"v{v1}" in diff

def test_resolve_conflict_creates_markers_and_activity():
    doc = Document()
    doc.edit("X", "alpha")
    v0 = doc.commit("v0")
    # Simulate second branch by editing and committing v1
    doc.edit("X", "beta")
    v1 = doc.commit("v1")
    # Now resolve between v0 and v1
    conflicts = doc.resolve_conflict(v0, v1)
    # Should report section "X" as conflict
    assert conflicts == ["X"]
    # Section content now contains conflict markers
    content = doc.sections["X"]
    assert "<<<<<<< v0" in content
    assert "alpha" in content
    assert "=======" in content
    assert "beta" in content
    # Activity recorded
    assert any("Resolved conflicts between versions 0 and 1" in e for e in doc.get_activity_feed())

def test_flush_operations_explicit_and_empty():
    doc = Document()
    # Flushing when no ops should still record
    doc.flush_operations()
    feed = doc.get_activity_feed()
    assert "Flushed operations" in feed
    # Now schedule an operation manually via edit (which auto flushes)
    doc.edit("Y", "hello")
    # queued_ops is empty due to autosave
    assert not doc.queued_ops
    # Manual flush again
    doc.flush_operations()
    assert "Flushed operations" in doc.get_activity_feed()

def test_lock_and_unlock_section():
    doc = Document()
    # Lock a section
    doc.lock_section("LockedSec")
    assert "Locked section 'LockedSec'" in doc.get_activity_feed()
    # Attempt to edit locked section
    with pytest.raises(ValueError):
        doc.edit("LockedSec", "should fail")
    # Unlock and then edit
    doc.unlock_section("LockedSec")
    doc.edit("LockedSec", "now works")
    assert doc.sections["LockedSec"] == "now works"
    assert any("Unlocked section 'LockedSec'" in e for e in doc.get_activity_feed())

def test_undo_reverts_to_last_commit():
    doc = Document()
    doc.edit("S", "v0")
    v0 = doc.commit("c0")
    doc.edit("S", "modified")
    # Now undo should revert to v0
    doc.undo()
    assert doc.sections["S"] == "v0"
    assert any("Undid to version 0" in e for e in doc.get_activity_feed())
    # Undo when no versions should error
    doc2 = Document()
    with pytest.raises(ValueError):
        doc2.undo()

def test_template_support_create_and_apply():
    doc = Document()
    doc.create_template("T1", "Template content")
    assert "Created template 'T1'" in doc.get_activity_feed()
    # Apply template
    doc.apply_template("SecTpl", "T1")
    # Section populated
    assert doc.sections["SecTpl"] == "Template content"
    assert any("Applied template 'T1' to section 'SecTpl'" in e for e in doc.get_activity_feed())
    # Applying non-existent template errors
    with pytest.raises(ValueError):
        doc.apply_template("X", "NoTpl")
