import pytest
from pipeline.backup import BackupAndRestore

def test_backup_and_restore(tmp_path):
    bak = BackupAndRestore()
    state = {'a': 1, 'b': 'test'}
    file = tmp_path / "state.json"
    bak.backup(state, str(file))
    assert file.exists()
    restored = bak.restore(str(file))
    assert restored == state
