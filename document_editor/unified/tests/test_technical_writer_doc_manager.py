import pytest
import difflib
import datetime
from doc_manager import DocumentManager, DocumentError, ConflictError


@pytest.fixture
def manager():
    return DocumentManager()


def test_create_and_commit_initial(manager):
    manager.create_document('doc1', {'sec1': 'hello', 'sec2': 'world'})
    # initial version should be 1
    doc = manager.documents['doc1']
    assert len(doc.versions) == 1
    assert doc.versions[0]['message'] == 'init'
    # commit does not error
    manager.commit('doc1', 'first commit')
    assert len(doc.versions) == 2
    assert doc.versions[1]['message'] == 'first commit'
    # activity feed contains create_document and commit
    ops = [e['operation'] for e in manager.activity_feed_all()]
    assert 'create_document' in ops
    assert 'commit' in ops


def test_autosave_and_flush(manager):
    manager.create_document('d2', {'a': '1', 'b': '2'})
    manager.autosave('d2', 'a', '1.1')
    # pending should exist
    doc = manager.documents['d2']
    assert len(doc.pending_ops) == 1
    # not yet applied
    assert doc.sections['a'] == '1'
    manager.flush_operations('d2')
    assert doc.sections['a'] == '1.1'
    # and pending cleared
    assert not doc.pending_ops


def test_edit_and_commit(manager):
    manager.create_document('d3', {'x': 'foo'})
    manager.edit('d3', 'x', 'bar')
    manager.commit('d3', 'update x')
    assert manager.documents['d3'].sections['x'] == 'bar'
    # version history
    versions = manager.documents['d3'].versions
    assert len(versions) == 2
    assert versions[-1]['content']['x'] == 'bar'


def test_version_compare(manager):
    manager.create_document('docX', {'s1': 'one\nline1\n', 's2': 'alpha\n'})
    manager.edit('docX', 's1', 'one\nline1\nadded\n')
    manager.commit('docX', 'v2')
    diffs = manager.version_compare('docX', 1, 2)
    # diffs for s1 should show 'added'
    assert 's1' in diffs
    dd = diffs['s1']
    assert any('added' in line for line in dd)
    # no diff in s2
    assert diffs['s2'] == []


def test_conflict_and_resolve(manager):
    manager.create_document('docC', {'sec': 'A'})
    # first edit locks sec
    manager.edit('docC', 'sec', 'B')
    # before flush or commit, another edit => conflict
    with pytest.raises(ConflictError):
        manager.edit('docC', 'sec', 'C')
    doc = manager.documents['docC']
    assert 'sec' in doc.conflicts
    # resolve conflict
    manager.resolve_conflict('docC', 'sec', 'Resolved')
    assert doc.sections['sec'] == 'Resolved'
    assert 'sec' not in doc.conflicts
    # now can edit again
    manager.edit('docC', 'sec', 'D')
    manager.flush_operations('docC')
    assert doc.sections['sec'] == 'D'


def test_unlock_section(manager):
    manager.create_document('d4', {'q': 'v'})
    manager.edit('d4', 'q', 'u')
    doc = manager.documents['d4']
    assert 'q' in doc.locks
    manager.unlock_section('d4', 'q')
    assert 'q' not in doc.locks


def test_undo_pending(manager):
    manager.create_document('d5', {'a': '0'})
    manager.edit('d5', 'a', '1')
    doc = manager.documents['d5']
    assert doc.pending_ops
    manager.undo('d5')
    # pending cleared
    assert not doc.pending_ops
    # section unchanged
    assert doc.sections['a'] == '0'


def test_undo_commit(manager):
    manager.create_document('d6', {'z': 'orig'})
    manager.edit('d6', 'z', 'new')
    manager.commit('d6', 'up1')
    doc = manager.documents['d6']
    assert doc.sections['z'] == 'new'
    manager.undo('d6')
    # reverted to orig
    assert doc.sections['z'] == 'orig'
    # versions back to 1
    assert len(doc.versions) == 1


def test_undo_nothing(manager):
    manager.create_document('d7', {'k': 'v'})
    with pytest.raises(DocumentError):
        manager.undo('d7')


def test_template_support(manager):
    manager.create_document('dt', {'s': 'X'})
    manager.create_template('tpl1', 'Template content')
    # applying non-existent template fails
    with pytest.raises(DocumentError):
        manager.apply_template('dt', 's', 'nope')
    # apply existing
    manager.apply_template('dt', 's', 'tpl1')
    doc = manager.documents['dt']
    # pending has apply_template
    assert any(op[0] == 'apply_template' for op in doc.pending_ops)
    # now flush & commit
    manager.flush_operations('dt')
    assert doc.sections['s'] == 'Template content'
    manager.commit('dt', 'applied tpl1')
    assert len(doc.versions) == 2


def test_activity_feed_contents(manager):
    manager.create_document('fa', {'p': '1'})
    manager.edit('fa', 'p', '2')
    manager.autosave('fa', 'p', '3')
    manager.flush_operations('fa')
    manager.commit('fa', 'msgs')
    feed = manager.activity_feed_all()
    ops = [e['operation'] for e in feed]
    expected = ['create_document', 'edit_queued', 'autosave_queued',
                'edit_flushed', 'autosave_flushed', 'commit']
    # ensure the expected ops appear in order as a subsequence
    idx = 0
    for op in ops:
        if idx < len(expected) and op == expected[idx]:
            idx += 1
    assert idx == len(expected)
