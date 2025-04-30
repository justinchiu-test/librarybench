import pytest
from content_repo import ContentRepo

@pytest.fixture
def repo():
    return ContentRepo()

def test_initial_state(repo):
    assert repo.head_commit == '0'
    assert repo.branches == {'main': '0'}
    assert repo.working_copy == {}
    assert repo.search("anything") == []

def test_edit_and_commit(repo):
    repo.edit("post1", "intro", "Hello World")
    cid1 = repo.commit("Add post1 intro")
    # after commit, head_commit updated
    assert repo.head_commit == cid1
    # commit state saved
    st = repo._commits[cid1].state
    assert "post1" in st
    assert st["post1"]["sections"]["intro"] == "Hello World"

def test_branch_and_checkout(repo):
    repo.edit("p", "s", "t")
    c0 = repo.commit("c0")
    repo.branch("dev")
    # dev points at c0
    assert repo.branches["dev"] == c0
    repo.checkout("dev")
    assert repo.head_branch == "dev"
    # make change on dev
    repo.edit("p", "s", "dev")
    c1 = repo.commit("dev change")
    assert repo.branches["dev"] == c1
    # switch back to main
    repo.checkout("main")
    assert repo.working_copy["p"]["sections"]["s"] == "t"

def test_detached_checkout(repo):
    repo.edit("x", "a", "1")
    c1 = repo.commit("c1")
    repo.checkout(c1)
    assert repo.head_branch is None
    assert repo.working_copy["x"]["sections"]["a"] == "1"
    with pytest.raises(ValueError):
        repo.commit("should fail")  # cannot commit in detached HEAD? actually we allow, but branch stays None
    # If desired, commit in detached still works but branch=None so new commit not tracked in branch

def test_comment_and_search(repo):
    repo.edit("post2", "body", "This is a test")
    repo.comment("post2", "body", "Needs more examples")
    cid = repo.commit("commented")
    st = repo._commits[cid].state
    assert "Needs more examples" in st["post2"]["comments"]["body"]
    # search finds by content, section, and comment
    assert "post2" in repo.search("test")
    assert "post2" in repo.search("body")
    assert "post2" in repo.search("examples")

def test_revert(repo):
    repo.edit("c1", "sec", "v1")
    c1 = repo.commit("v1")
    repo.edit("c1", "sec", "v2")
    # now working_copy has v2
    assert repo.working_copy["c1"]["sections"]["sec"] == "v2"
    # revert to c1
    repo.revert("c1", c1)
    assert repo.working_copy["c1"]["sections"]["sec"] == "v1"
    # cannot revert from unknown commit
    with pytest.raises(ValueError):
        repo.revert("c1", "999")

def test_snapshot(repo):
    repo.edit("a", "s", "t")
    c = repo.commit("one")
    repo.snapshot("v1", c)
    assert repo.tags["v1"] == c
    assert "v1" in repo._commits[c].tags
    with pytest.raises(ValueError):
        repo.snapshot("v1", c)  # duplicate tag

def test_merge_and_diff(repo):
    # setup main
    repo.edit("X", "sec", "main")
    m1 = repo.commit("m1")
    # branch dev
    repo.branch("dev")
    repo.checkout("dev")
    repo.edit("X", "sec", "dev")
    d1 = repo.commit("dev1")
    # switch back and change main
    repo.checkout("main")
    repo.edit("X", "sec2", "m2")
    m2 = repo.commit("m2")
    # merge dev into main
    mid = repo.merge("dev", "main")
    # merged should have sec from dev and sec2 from main
    wc = repo.working_copy
    assert wc["X"]["sections"]["sec"] == "dev"
    assert wc["X"]["sections"]["sec2"] == "m2"
    # merge commit parents
    parents = repo._commits[mid].parents
    assert set(parents) == {m2, d1}
    # diff between m1 and m2 on X
    diff = repo.diff("X", m1, m2)
    # sec added in main branch
    assert diff["sections"]["sec2"] == (None, "m2")
    # diff between m1 and d1
    diff2 = repo.diff("X", m1, d1)
    assert diff2["sections"]["sec"] == ("main", "dev")
    # diff unknown commit
    with pytest.raises(ValueError):
        repo.diff("X", "0", "999")

def test_merge_conflict_comments(repo):
    # test that comments get merged
    repo.edit("Z", "a", "1")
    c1 = repo.commit("c1")
    repo.branch("b1")
    repo.branch("b2")
    repo.checkout("b1")
    repo.comment("Z", "a", "cmt1")
    d1 = repo.commit("d1")
    repo.checkout("b2")
    repo.comment("Z", "a", "cmt2")
    d2 = repo.commit("d2")
    # merge b2 into b1
    repo.merge("b2", "b1")
    cmts = repo.working_copy["Z"]["comments"]["a"]
    assert "cmt1" in cmts and "cmt2" in cmts

def test_search_multiple(repo):
    repo.edit("one", "title", "Hello")
    repo.edit("two", "title", "World")
    repo.comment("one", "title", "Note")
    res = repo.search("hello")
    assert res == ["one"]
    res2 = set(repo.search("title"))
    assert res2 == {"one", "two"}
