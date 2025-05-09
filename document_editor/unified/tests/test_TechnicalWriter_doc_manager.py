import os
import tempfile
import pytest
from doc_manager import Document


def test_initial_commit_and_log():
    doc = Document("TestDoc")
    logs = doc.log()
    assert len(logs) == 1
    assert logs[0]["message"] == "Initial commit"
    # head != None
    assert "id" in logs[0]


def test_commit_creates_new_id_and_logs():
    doc = Document("D")
    first_id = doc.log()[0]["id"]
    # add a section manually
    doc.branches["main"]["working"]["intro"] = "Hello"
    new_id = doc.commit("add intro")
    assert new_id != first_id
    logs = doc.log()
    assert logs[0]["id"] == new_id
    assert logs[0]["message"] == "add intro"
    assert logs[1]["id"] == first_id


def test_branching_and_isolation():
    doc = Document("D")
    # modify main
    doc.branches["main"]["working"]["sec1"] = "A"
    m1 = doc.commit("m1")
    # branch off
    doc.branch("dev")
    # modify dev
    doc.branches["dev"]["working"]["sec1"] = "DEV"
    d1 = doc.commit("dev change", branch="dev")
    # main still has "A"
    main_head = doc.commits[doc.branches["main"]["head"]].content
    dev_head = doc.commits[doc.branches["dev"]["head"]].content
    assert main_head["sec1"] == "A"
    assert dev_head["sec1"] == "DEV"
    # logs differ
    assert len(doc.log(branch="main")) == 2
    assert len(doc.log(branch="dev")) == 3  # initial, m1, dev change


def test_templates_apply_and_commit():
    doc = Document("D")
    doc.create_template("t1", "Template Content")
    doc.apply_template("t1", "outline")
    with pytest.raises(ValueError):
        # nonexistent template
        doc.apply_template("nope", "x")
    cid = doc.commit("apply t1")
    content = doc.commits[cid].content
    assert content["outline"] == "Template Content"


def test_import_content(tmp_path):
    f = tmp_path / "data.txt"
    f.write_text("Imported Text")
    doc = Document("D")
    doc.import_content(str(f), "ext")
    with pytest.raises(ValueError):
        doc.import_content("no_such_file.txt", "x")
    cid = doc.commit("import")
    assert doc.commits[cid].content["ext"] == "Imported Text"


def test_snapshot_and_checkout():
    doc = Document("D")
    doc.branches["main"]["working"]["a"] = "1"
    c1 = doc.commit("c1")
    doc.branches["main"]["working"]["a"] = "2"
    c2 = doc.commit("c2")
    doc.snapshot("v1")
    # move on
    doc.branches["main"]["working"]["a"] = "3"
    c3 = doc.commit("c3")
    # checkout by label
    doc.checkout("v1")
    head = doc.branches["main"]["head"]
    assert head == c2
    assert doc.branches["main"]["working"]["a"] == "2"
    # checkout by id
    doc.checkout(c1)
    assert doc.branches["main"]["head"] == c1
    assert doc.branches["main"]["working"]["a"] == "1"
    with pytest.raises(ValueError):
        doc.checkout("nope")


def test_merge_naive():
    doc = Document("D")
    # setup main
    doc.branches["main"]["working"]["x"] = "M"
    main1 = doc.commit("main1")
    # branch dev
    doc.branch("dev")
    doc.branches["dev"]["working"]["y"] = "D"
    dev1 = doc.commit("dev1", branch="dev")
    # change main too
    doc.branches["main"]["working"]["z"] = "M2"
    main2 = doc.commit("main2")
    # merge dev into main
    m = doc.merge("dev", "main", message="merge dev")
    content = doc.commits[m].content
    assert content["x"] == "M"
    assert content["y"] == "D"
    assert content["z"] == "M2"
    assert doc.commits[m].message == "merge dev"


def test_collaborators_and_locking():
    doc = Document("D")
    assert doc.list_collaborators() == []
    doc.add_collaborator("Alice")
    doc.add_collaborator("Bob")
    lst = doc.list_collaborators()
    assert set(lst) == {"Alice", "Bob"}
    doc.remove_collaborator("Alice")
    assert doc.list_collaborators() == ["Bob"]
    with pytest.raises(ValueError):
        doc.remove_collaborator("Nope")
    # lock a section
    doc.branches["main"]["working"]["sec"] = "OK"
    cid = doc.commit("init sec")
    doc.lock_section("sec")
    # modify locked section
    doc.branches["main"]["working"]["sec"] = "BAD"
    with pytest.raises(ValueError):
        doc.commit("try bad")
    # but other sections are ok
    doc.branches["main"]["working"]["sec"] = "OK"
    doc.branches["main"]["working"]["fine"] = "good"
    new = doc.commit("ok")
    assert "fine" in doc.commits[new].content
