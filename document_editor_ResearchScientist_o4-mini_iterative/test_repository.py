import os
import tempfile
import pytest
from research_vcs import Repository

@pytest.fixture
def repo():
    return Repository()

def test_initial_commit(repo):
    log = repo.log()
    assert len(log) == 1
    assert log[0].id == "0"
    assert log[0].message == "root"

def test_commit_and_log(repo):
    cid1 = repo.commit("First commit")
    cid2 = repo.commit("Second commit")
    logs = repo.log()
    assert [c.id for c in logs] == [cid2, cid1, "0"]
    assert logs[0].message == "Second commit"
    assert logs[1].message == "First commit"

def test_branching(repo):
    repo.commit("C1")
    repo.branch("dev")
    # commit on main
    cm = repo.commit("main work")
    # switch to dev branch by checkout pointer
    repo.current_branch = "dev"
    cd = repo.commit("dev work")
    # logs
    log_main = repo.log("main")
    assert log_main[0].message == "main work"
    log_dev = repo.log("dev")
    assert log_dev[0].message == "dev work"
    # ensure branches diverged
    assert log_main[0].id != log_dev[0].id

def test_import_section(tmp_path, repo):
    # create a temp file
    p = tmp_path / "data.txt"
    p.write_text("experiment results")
    repo.import_section("Results", str(p))
    assert repo.sections["Results"] == "experiment results"
    # lock and then fail import
    repo.lock_section("Results")
    with pytest.raises(ValueError):
        repo.import_section("Results", str(p))
    with pytest.raises(ValueError):
        repo.import_section("Unknown", "no_file.txt")

def test_snapshot_and_checkout(repo):
    repo.sections["Intro"] = "v1"
    c1 = repo.commit("intro v1")
    repo.snapshot("draft1")
    # change and commit
    repo.sections["Intro"] = "v2"
    c2 = repo.commit("intro v2")
    assert repo.sections["Intro"] == "v2"
    # checkout snapshot
    repo.checkout("draft1")
    # head should be c1
    head = repo.branches[repo.current_branch]
    assert head == c1
    assert repo.sections["Intro"] == "v1"
    # unknown snapshot
    with pytest.raises(ValueError):
        repo.checkout("no_label")
    with pytest.raises(ValueError):
        repo.checkout("999")

def test_snapshot_duplicate(repo):
    repo.snapshot("a")
    with pytest.raises(ValueError):
        repo.snapshot("a")

def test_merge(repo):
    # initial commits
    repo.sections["A"] = "1"
    repo.commit("set A1")
    repo.branch("feature")
    # main branch
    repo.sections["B"] = "main-B"
    repo.commit("set B-main")
    # switch to feature
    repo.current_branch = "feature"
    repo.sections["A"] = "feat-A"
    repo.commit("feat A")
    # back to main
    repo.current_branch = "main"
    # merge feature into main
    merge_cid = repo.merge("feature", "main")
    # head of main is merge_cid
    assert repo.branches["main"] == merge_cid
    # both A from feature and B from main present
    assert repo.sections["A"] == "feat-A"
    assert repo.sections["B"] == "main-B"

def test_merge_nonexistent_branch(repo):
    with pytest.raises(ValueError):
        repo.merge("no", "main")
    with pytest.raises(ValueError):
        repo.merge("main", "no")

def test_collaborators(repo):
    repo.add_collaborator("Alice")
    repo.add_collaborator("Bob")
    assert set(repo.list_collaborators()) == {"Alice", "Bob"}
    with pytest.raises(ValueError):
        repo.add_collaborator("Alice")
    repo.remove_collaborator("Alice")
    assert repo.list_collaborators() == ["Bob"]
    with pytest.raises(ValueError):
        repo.remove_collaborator("Alice")

def test_lock_and_template(repo):
    tpl = {
        "Intro": "Template intro",
        "Methods": "Template methods"
    }
    repo.create_template("std", tpl)
    repo.apply_template("std")
    assert repo.sections["Intro"] == "Template intro"
    # lock Intro and fail reapply
    repo.lock_section("Intro")
    tpl2 = {"Intro": "New intro"}
    repo.create_template("alt", tpl2)
    with pytest.raises(ValueError):
        repo.apply_template("alt")
    with pytest.raises(ValueError):
        repo.create_template("std", tpl)

def test_checkout_branch_preserves_branch(repo):
    # ensure checkout doesn't switch branches
    repo.sections["X"] = "x1"
    c1 = repo.commit("x1")
    repo.sections["X"] = "x2"
    c2 = repo.commit("x2")
    repo.snapshot("two")
    # now checkout to c1
    repo.checkout(c1)
    assert repo.sections["X"] == "x1"
    assert repo.current_branch == "main"

def test_commit_returns_id(repo):
    c = repo.commit("msg")
    assert isinstance(c, str)
    assert c in repo.commits
