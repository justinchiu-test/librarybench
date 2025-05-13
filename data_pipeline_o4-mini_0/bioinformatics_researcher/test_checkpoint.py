from pipeline.checkpoint import CheckpointManager

def test_checkpoint_manager():
    cp = CheckpointManager()
    cp.save('key1', 123)
    assert cp.load('key1') == 123
    assert cp.load('nonexistent') is None
