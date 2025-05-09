import pytest
from doc_manager import DocumentManager

def test_autosave_and_last_autosave():
    dm = DocumentManager({"sec1": "content1"})
    dm.edit("sec1", "new")
    dm.flush_operations()
    autosaved = dm.autosave()
    assert autosaved == {"sec1": "new"}
    # modify after autosave
    dm.edit("sec2", "content2")
    dm.flush_operations()
    # last_autosave remains previous
    assert dm.last_autosave == {"sec1": "new"}
    assert dm.document == {"sec1": "new", "sec2": "content2"}

def test_edit_and_flush_operations_and_activity_feed():
    dm = DocumentManager({"a": "1", "b": "2"})
    dm.edit("a", "one")
    dm.edit("c", "three")
    # activity_feed should have queued messages
    feed = dm.activity_feed()
    assert "Queued edit on 'a'" in feed
    assert "Queued edit on 'c'" in feed
    # flush
    assert dm.flush_operations() is True
    # document updated
    assert dm.document == {"a": "one", "b": "2", "c": "three"}
    # activity_feed has applied operations
    feed = dm.activity_feed()
    assert "edit applied: ('a', 'one')" in feed
    assert "edit applied: ('c', 'three')" in feed

def test_commit_and_version_compare():
    dm = DocumentManager({"x": "X"})
    dm.commit("initial")
    dm.edit("x", "Y")
    dm.flush_operations()
    dm.commit("changed x")
    assert len(dm.commit_history) == 2
    diffs = dm.version_compare(0, 1)
    assert diffs == {"x": ("X", "Y")}
    # same version yields empty diff
    assert dm.version_compare(1, 1) == {}

def test_version_compare_out_of_range():
    dm = DocumentManager()
    with pytest.raises(IndexError):
        dm.version_compare(0, 1)

def test_resolve_conflict():
    dm = DocumentManager({"k": "v1", "unchanged": "u"})
    dm.commit("ver1")
    dm.edit("k", "v2")
    dm.flush_operations()
    dm.edit("new", "n")
    dm.flush_operations()
    dm.commit("ver2")
    merged = dm.resolve_conflict(0, 1)
    # choose version1 changes (v2) and new
    assert merged["k"] == "v2"
    assert merged["new"] == "n"
    assert merged["unchanged"] == "u"
    # document updated
    assert dm.document == merged

def test_undo_edit():
    dm = DocumentManager({"s": "old"})
    dm.edit("s", "new")
    dm.flush_operations()
    assert dm.document["s"] == "new"
    dm.undo()
    # restored
    assert dm.document["s"] == "old"
    # activity_feed has undo entry
    assert "undo edit: ('s', 'new')" in dm.activity_feed()

def test_undo_without_operations():
    dm = DocumentManager()
    with pytest.raises(RuntimeError):
        dm.undo()

def test_unlock_section_and_edit_locked():
    dm = DocumentManager({"sec": "c"})
    # lock section manually
    dm.locked_sections.add("sec")
    dm.edit("sec", "new")
    with pytest.raises(RuntimeError):
        dm.flush_operations()
    # clear queue
    dm.operation_queue.clear()
    # unlock then edit
    dm.unlock_section("sec")
    dm.flush_operations()
    assert "sec" not in dm.locked_sections
    dm.edit("sec", "new")
    dm.flush_operations()
    assert dm.document["sec"] == "new"

def test_template_support_and_apply_and_undo():
    dm = DocumentManager({"a": "1"})
    template = {"b": "B", "a": "A_template"}
    dm.create_template("tpl1", template)
    assert "tpl1" in dm.templates
    assert "create_template 'tpl1'" in dm.activity_feed()
    dm.apply_template("tpl1")
    dm.flush_operations()
    assert dm.document["b"] == "B"
    assert dm.document["a"] == "A_template"
    # undo apply_template
    dm.undo()
    # should restore to before template
    assert dm.document == {"a": "1"}

def test_flush_order_and_undo_sequence():
    dm = DocumentManager({"m": "M"})
    # lock m, then queue operations
    dm.locked_sections.add("m")
    dm.edit("n", "N")
    dm.unlock_section("m")
    dm.edit("m", "MM")
    dm.flush_operations()
    # after flush: both edits and unlock applied
    assert dm.document == {"m": "MM", "n": "N"}
    # undo last (edit m)
    dm.undo()
    assert dm.document == {"m": "M", "n": "N"}
    # undo unlock_section
    dm.undo()
    assert "m" in dm.locked_sections
    # undo first edit
    dm.undo()
    assert "n" not in dm.document
    # no more undo
    with pytest.raises(RuntimeError):
        dm.undo()
