import pytest
import difflib
from vcs import Repository, Commit


def test_initial_state():
    repo = Repository()
    # initial commit id is "0"
    assert repo.HEAD.id == "0"
    assert repo.current_branch.name == "main"
    assert repo.working_directory == {}
    assert repo.commits["0"].message == "initial commit"


def test_edit_and_commit():
    repo = Repository()
    repo.edit("script.py", "print('hello')\n")
    assert "script.py" in repo.working_directory
    repo.commit("add script")
    c1 = repo.HEAD
    assert c1.message == "add script"
    assert c1.snapshot["script.py"] == "print('hello')\n"
    # edit and commit again
    repo.edit("script.py", "print('world')\n", append=True)
    repo.commit("append world")
    c2 = repo.HEAD
    expected = "print('hello')\nprint('world')\n"
    assert c2.snapshot["script.py"] == expected


def test_branch_and_checkout():
    repo = Repository()
    repo.edit("data.txt", "A\n")
    repo.commit("A")
    repo.branch("dev")
    repo.checkout("dev")
    # on dev branch, edit differently
    repo.edit("data.txt", "B\n", append=True)
    repo.commit("B")
    assert repo.current_branch.name == "dev"
    assert "B" in repo.HEAD.snapshot["data.txt"]
    # switch back
    repo.checkout("main")
    assert repo.current_branch.name == "main"
    # main should not have B
    assert "B" not in repo.working_directory["data.txt"]


def test_revert():
    repo = Repository()
    repo.edit("f.txt", "v1\n")
    repo.commit("v1")
    repo.edit("f.txt", "v2\n", append=True)
    repo.commit("v2")
    # revert last commit
    repo.revert()
    # HEAD should be v1 commit
    assert repo.HEAD.message == "v1"
    assert repo.working_directory["f.txt"] == "v1\n"


def test_comment_top_and_bottom():
    repo = Repository()
    repo.edit("x.py", "print(1)\n")
    repo.comment("x.py", "hello", position="top")
    assert repo.working_directory["x.py"].startswith("# hello\n")
    repo.comment("x.py", "bye", position="bottom")
    assert repo.working_directory["x.py"].endswith("# bye\n")


def test_search():
    repo = Repository()
    repo.edit("a.txt", "foo\nbaz\n")
    repo.edit("b.txt", "bar\nfoo\n")
    res = repo.search("foo")
    # two occurrences
    assert ("a.txt", 1, "foo") in res
    assert ("b.txt", 2, "foo") in res


def test_snapshot_and_checkout_tag():
    repo = Repository()
    repo.edit("t.txt", "X\n")
    repo.commit("X")
    repo.snapshot("v1")
    # modify
    repo.edit("t.txt", "Y\n", append=True)
    repo.commit("Y")
    assert "Y" in repo.working_directory["t.txt"]
    # checkout tag
    repo.checkout("v1")
    # working dir returns to X
    assert repo.working_directory["t.txt"] == "X\n"
    # HEAD is tag commit
    assert repo.HEAD.message == "X"


def test_merge_no_conflict():
    repo = Repository()
    # base
    repo.edit("f1", "base\n")
    repo.commit("base")
    # branch dev
    repo.branch("dev")
    repo.checkout("dev")
    repo.edit("f2", "branch\n")
    repo.commit("branch work")
    # switch to main and merge dev
    repo.checkout("main")
    m = repo.merge("dev")
    assert isinstance(m, Commit)
    # f2 should now exist
    assert repo.working_directory["f2"] == "branch\n"
    # merge commit has two parents
    assert len(m.parents) == 2


def test_merge_conflict():
    repo = Repository()
    # base write file
    repo.edit("conf", "line1\n")
    repo.commit("base")
    # branch dev edits differently
    repo.branch("dev")
    repo.checkout("dev")
    repo.edit("conf", "dev line\n")
    repo.commit("dev change")
    # back to main, edit differently
    repo.checkout("main")
    repo.edit("conf", "main line\n")
    repo.commit("main change")
    # merge dev into main => conflict
    m = repo.merge("dev")
    merged = repo.working_directory["conf"]
    assert "<<<<<<< HEAD" in merged
    assert "main line\n" in merged
    assert "dev line\n" in merged
    # parents are main head and dev head
    assert len(m.parents) == 2


def test_diff_between_commits_and_working():
    repo = Repository()
    repo.edit("d.txt", "one\n")
    repo.commit("one")
    c1 = repo.HEAD.id
    repo.edit("d.txt", "two\n", append=True)
    # diff between c1 and working
    diffs = repo.diff(a=c1)
    # should show addition of "two\n"
    diffstr = "".join(diffs)
    assert "+two\n" in diffstr
    # diff between two commits
    repo.commit("two")
    c2 = repo.HEAD.id
    diffs2 = repo.diff(a=c1, b=c2)
    s2 = "".join(diffs2)
    assert "+two\n" in s2
