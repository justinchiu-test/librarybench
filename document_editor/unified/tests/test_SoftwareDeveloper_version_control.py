import pytest
from version_control import (
    Repo,
    unlock_section, edit, collaborator_list,
    add_collaborator, remove_collaborator,
    history_view, apply_operation, resolve_conflict,
    template_support, branch, checkout, redo, undo, commit
)

def test_collaborators():
    r = Repo()
    assert collaborator_list(r) == []
    add_collaborator(r, "alice")
    add_collaborator(r, "bob")
    lst = collaborator_list(r)
    assert "alice" in lst and "bob" in lst
    remove_collaborator(r, "alice")
    assert collaborator_list(r) == ["bob"]

def test_unlock_and_edit_sections():
    r = Repo()
    # artificially lock a section
    r.locked_sections["file1"] = {"sec1"}
    # editing locked section should fail
    with pytest.raises(Exception):
        edit(r, "file1", "new code", section_id="sec1")
    # unlock and then edit should succeed
    unlock_section(r, "file1", "sec1")
    edit(r, "file1", "new code", section_id="sec1")
    assert r.files["file1"] == "new code"

def test_simple_edit_and_commit_history():
    r = Repo()
    # initial file
    edit(r, "a.txt", "line1")
    c1 = commit(r, "first")
    assert isinstance(c1, str) and "main-0" in c1
    # change and commit again
    edit(r, "a.txt", "line2")
    c2 = commit(r, "second")
    assert history_view(r) == ["first", "second"]
    # files reflect last commit
    assert r.files["a.txt"] == "line2"

def test_apply_operation_immutability():
    r = Repo()
    edit(r, "f.txt", "orig")
    def op(repo):
        edit(repo, "f.txt", "changed")
    r2 = apply_operation(r, op)
    # original untouched
    assert r.files["f.txt"] == "orig"
    # new repo has change but no commit history
    assert r2.files["f.txt"] == "changed"
    assert history_view(r2) == []
    # original history still empty
    assert history_view(r) == []

def test_resolve_conflict_keeps_ours():
    r = Repo()
    conflicted = "\n".join([
        "start",
        "<<<<<<< HEAD",
        "ours line",
        "=======",
        "theirs line",
        ">>>>>>> branch",
        "end"
    ])
    edit(r, "conf.txt", conflicted)
    resolve_conflict(r, "conf.txt")
    # after resolution we get start, ours line, end
    assert r.files["conf.txt"].splitlines() == ["start", "ours line", "end"]

def test_template_support_set_and_get():
    r = Repo()
    assert template_support(r, "tpl1") is None
    template_support(r, "tpl1", "code skeleton")
    assert template_support(r, "tpl1") == "code skeleton"

def test_branch_and_checkout_and_commit():
    r = Repo()
    edit(r, "x", "v1")
    c0 = commit(r, "v1")
    # create branch feature
    branch(r, "feature")
    # on same branch until checkout
    edit(r, "x", "v2")
    c1 = commit(r, "v2")
    # go to feature (which only has c0)
    checkout(r, "feature")
    assert history_view(r) == ["v1"]
    assert r.files["x"] == "v1"
    # commit in feature
    edit(r, "x", "feat")
    cf = commit(r, "feat")
    assert history_view(r) == ["v1", "feat"]
    # switch back to main
    checkout(r, "main")
    assert history_view(r) == ["v1", "v2"]
    assert r.files["x"] == "v2"
    # checkout specific commit
    checkout(r, c0)
    assert r.files["x"] == "v1"

def test_undo_and_redo():
    r = Repo()
    edit(r, "a", "one")
    c1 = commit(r, "one")
    edit(r, "a", "two")
    c2 = commit(r, "two")
    assert history_view(r) == ["one", "two"]
    # undo last commit
    u = undo(r)
    assert u == c2
    assert history_view(r) == ["one"]
    assert r.files.get("a") == "one"
    # now redo
    rd = redo(r)
    assert rd == c2
    assert history_view(r) == ["one", "two"]
    assert r.files["a"] == "two"
    # undo everything
    undo(r)
    undo(r)
    with pytest.raises(Exception):
        undo(r)  # nothing left to undo
    # redo twice
    rd1 = redo(r)
    rd2 = redo(r)
    assert history_view(r) == ["one", "two"]
    with pytest.raises(Exception):
        redo(r)  # nothing to redo

def test_invalid_checks():
    r = Repo()
    with pytest.raises(Exception):
        checkout(r, "nonexistent")
    with pytest.raises(Exception):
        branch(r, "main")  # already exists
    with pytest.raises(Exception):
        redo(r)  # nothing undone

