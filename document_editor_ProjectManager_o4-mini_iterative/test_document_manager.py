import pytest
from document_manager import DocumentManager

def test_collaborators():
    dm = DocumentManager()
    assert dm.collaborator_list() == []
    dm.add_collaborator('alice')
    assert 'alice' in dm.collaborator_list()
    dm.add_collaborator('bob')
    assert set(dm.collaborator_list()) == {'alice', 'bob'}
    assert dm.remove_collaborator('alice') is True
    assert 'alice' not in dm.collaborator_list()
    assert dm.remove_collaborator('charlie') is False

def test_resolve_conflict_and_log():
    dm = DocumentManager()
    res = dm.resolve_conflict('section1', 'value1')
    assert res is True
    assert dm.conflicts['section1'] == 'value1'
    assert any('resolve_conflict section1=value1' in entry for entry in dm.log())

def test_activity_feed_records_actions():
    dm = DocumentManager()
    dm.add_collaborator('alice')
    dm.resolve_conflict('k', 'v')
    feed = dm.activity_feed()
    assert any('add_collaborator alice' in entry for entry in feed)
    assert any('resolve_conflict k=v' in entry for entry in feed)

def test_comment_and_notifications_and_log():
    dm = DocumentManager()
    dm.add_collaborator('alice')
    dm.add_collaborator('bob')
    with pytest.raises(ValueError):
        dm.comment('sec1', 'charlie', 'hi')
    dm.comment('sec1', 'alice', 'Looks good')
    assert 'sec1' in dm.comments
    assert dm.comments['sec1'] == [('alice', 'Looks good')]
    for user in ['alice', 'bob']:
        notifs = dm.notifications(user)
        assert any('commented on sec1' in msg for msg in notifs)
    assert any('comment alice@sec1: Looks good' in entry for entry in dm.log())

def test_lock_and_unlock_section_and_log():
    dm = DocumentManager()
    dm.lock_section('sec1')
    assert 'sec1' in dm.locked_sections
    assert dm.unlock_section('sec1') is True
    assert 'sec1' not in dm.locked_sections
    assert dm.unlock_section('unknown') is False
    log = dm.log()
    assert any('lock_section sec1' in e for e in log)
    assert any('unlock_section sec1' in e for e in log)

def test_snapshot_and_version_compare():
    init_text = "hello\nworld"
    dm = DocumentManager(init_text)
    dm.apply_operation({'type':'insert', 'position':5, 'text':' everyone'})
    dm.snapshot('greeting')
    assert 'greeting' in dm.snapshots
    ver = dm.snapshots['greeting']
    assert ver == dm.current_version
    diff = dm.version_compare(0, ver)
    # Expect lines showing the insertion of " everyone"
    assert any('+hello everyone' in line or '+hello everyoneworld' in line or '+world' in line for line in diff)
    with pytest.raises(ValueError):
        dm.version_compare(0, 999)

def test_apply_operations_and_content_and_version_and_log():
    dm = DocumentManager("abcd")
    dm.add_collaborator('alice')
    assert dm.apply_operation({'type':'insert', 'position':2, 'text':'X'}) is True
    assert dm.content == 'abXcd'
    v1 = dm.current_version
    assert dm.versions[v1] == 'abXcd'
    assert dm.apply_operation({'type':'delete', 'position':1, 'length':2}) is True
    assert dm.content == 'acd'
    assert dm.apply_operation({'type':'edit', 'position':1, 'length':2, 'text':'YZ'}) is True
    assert dm.content == 'aYZd'
    with pytest.raises(ValueError):
        dm.apply_operation({'type':'unknown'})
    assert any('apply_operation' in e for e in dm.log())

def test_notifications_all():
    dm = DocumentManager()
    dm.add_collaborator('alice')
    dm.add_collaborator('bob')
    dm.apply_operation({'type':'insert', 'position':0, 'text':'Hello'})
    all_notifs = dm.notifications()
    assert 'alice' in all_notifs and 'bob' in all_notifs
    assert any('Operation applied' in msg for msg in all_notifs['alice'])

def test_log_history_order():
    dm = DocumentManager()
    dm.add_collaborator('alice')
    dm.resolve_conflict('a', 'b')
    dm.apply_operation({'type':'insert', 'position':0, 'text':'hi'})
    log = dm.log()
    assert log[0].startswith('add_collaborator')
    assert log[1].startswith('resolve_conflict')
    assert log[2].startswith('apply_operation')
