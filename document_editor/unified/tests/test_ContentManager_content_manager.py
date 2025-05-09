import os
import tempfile
import pytest
from content_manager import ContentManager

def test_commit_and_log_sequence():
    cm = ContentManager()
    # no commits yet
    assert cm.log() == []
    # commit twice
    id1 = cm.commit("Initial draft")
    id2 = cm.commit("Added introduction")
    history = cm.log()
    assert len(history) == 2
    assert history[0] == (id1, "Initial draft")
    assert history[1] == (id2, "Added introduction")
    # messages preserved
    assert history[1][1] == "Added introduction"

def test_branch_and_switch():
    cm = ContentManager()
    cm.commit("base")
    cm.branch("feature")
    # switch
    cm.switch_branch("feature")
    # commit on feature
    fid = cm.commit("feature work")
    assert cm.log()[-1] == (fid, "feature work")
    # switch back
    cm.switch_branch("main")
    assert len(cm.log()) == 1
    assert cm.log()[0][1] == "base"
    with pytest.raises(ValueError):
        cm.switch_branch("nonexistent")

def test_snapshot_and_checkout_by_id_and_label():
    cm = ContentManager()
    cm.commit("v1")
    cm.commit("v2")
    commits = cm.log()
    id_v1, _ = commits[0]
    # snapshot label
    label_id = cm.snapshot("release1")
    assert label_id == cm.log()[-1][0]
    # make another commit
    id_v3 = cm.commit("v3")
    # checkout by id
    ret = cm.checkout(id_v1)
    assert ret == id_v1
    # state should match v1: no throw means success
    # checkout by label
    ret2 = cm.checkout("release1")
    assert ret2 == label_id
    # invalid checkout
    with pytest.raises(ValueError):
        cm.checkout("badlabel")

def test_import_content(tmp_path):
    cm = ContentManager()
    # create tmp file
    f = tmp_path / "data.txt"
    f.write_text("hello world")
    sec = cm.import_content(str(f))
    assert sec == "data.txt"
    # content stored
    branch = cm.branches[cm.current_branch]
    assert branch.sections["data.txt"] == "hello world"
    # import to named section
    f2 = tmp_path / "more.txt"
    f2.write_text("more data")
    sec2 = cm.import_content(str(f2), section_name="sec2")
    assert sec2 == "sec2"
    assert branch.sections["sec2"] == "more data"
    # lock and then import should fail
    cm.lock_section("sec2")
    with pytest.raises(ValueError):
        cm.import_content(str(f2), section_name="sec2")
    # non-existent file
    with pytest.raises(FileNotFoundError):
        cm.import_content("no_file.txt")

def test_template_support_and_apply():
    cm = ContentManager()
    # add a section
    cm.branches[cm.current_branch].sections["sec"] = "body"
    # create template
    cm.create_template("tpl", "<h1>", "</h1>")
    # apply
    cm.apply_template("tpl", "sec")
    assert cm.branches[cm.current_branch].sections["sec"] == "<h1>body</h1>"
    # applying to non-existent template
    with pytest.raises(ValueError):
        cm.apply_template("no", "sec")
    # applying to non-existent section
    with pytest.raises(ValueError):
        cm.apply_template("tpl", "none")
    # lock then apply
    cm.branches[cm.current_branch].sections["locked"] = "text"
    cm.lock_section("locked")
    with pytest.raises(ValueError):
        cm.apply_template("tpl", "locked")
    # duplicate template creation
    with pytest.raises(ValueError):
        cm.create_template("tpl", "", "")

def test_collaborators_management():
    cm = ContentManager()
    assert cm.collaborator_list() == []
    cm.add_collaborator("alice")
    cm.add_collaborator("bob")
    lst = cm.collaborator_list()
    assert set(lst) == {"alice", "bob"}
    cm.remove_collaborator("alice")
    assert cm.collaborator_list() == ["bob"]
    with pytest.raises(ValueError):
        cm.remove_collaborator("charlie")

def test_lock_section_errors_and_behavior():
    cm = ContentManager()
    # lock non-existent section
    with pytest.raises(ValueError):
        cm.lock_section("no")
    # add and lock
    cm.branches[cm.current_branch].sections["s"] = "x"
    cm.lock_section("s")
    # locked section in state
    assert "s" in cm.branches[cm.current_branch].locks

def test_merge_branches():
    cm = ContentManager()
    # on main, add section A and commit
    cm.branches["main"].sections["A"] = "1"
    cm.commit("commit A1")
    # branch off feature
    cm.branch("feature")
    # modify on feature
    cm.switch_branch("feature")
    cm.branches["feature"].sections["A"] = "2"
    cm.branches["feature"].sections["B"] = "new"
    cm.commit("feature changes")
    fid = cm.log()[-1][0]
    # lock B on main
    cm.switch_branch("main")
    cm.branches["main"].sections["B"] = "origB"
    cm.lock_section("B")
    # merge feature into main
    cm.merge("feature", "main")
    # A should be updated, B should remain origB because locked
    main_sec = cm.branches["main"].sections
    assert main_sec["A"] == "2"
    assert main_sec["B"] == "origB"
    # merging from non-existent branch
    with pytest.raises(ValueError):
        cm.merge("no", "main")
    with pytest.raises(ValueError):
        cm.merge("feature", "no")

def test_checkout_resets_state_and_locks():
    cm = ContentManager()
    # add and lock a section, commit
    cm.branches["main"].sections["X"] = "v1"
    cm.lock_section("X")
    id1 = cm.commit("c1")
    # change X and unlock in working copy
    cm.branches["main"].sections["X"] = "v2"
    # checkout id1
    cm.checkout(id1)
    # state and locks restored
    branch = cm.branches["main"]
    assert branch.sections["X"] == "v1"
    assert "X" in branch.locks

def test_log_after_branching_and_commits():
    cm = ContentManager()
    cm.commit("m1")
    cm.commit("m2")
    cm.branch("dev")
    cm.switch_branch("dev")
    cm.commit("d1")
    log_dev = cm.log()
    assert len(log_dev) == 3
    assert log_dev[-1][1] == "d1"
    cm.switch_branch("main")
    log_main = cm.log()
    assert len(log_main) == 2
