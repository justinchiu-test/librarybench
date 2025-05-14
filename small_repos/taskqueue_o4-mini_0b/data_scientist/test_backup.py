from ml_pipeline.backup import snapshot, restore

def test_snapshot_restore(tmp_path):
    data = {"a": 1, "b": 2}
    path = tmp_path / "state.pkl"
    snapshot(data, str(path))
    loaded = restore(str(path))
    assert loaded == data
