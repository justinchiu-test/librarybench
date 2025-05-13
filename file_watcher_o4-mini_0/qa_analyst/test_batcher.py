from watcher.batcher import EventBatcher

def test_batcher():
    b = EventBatcher(batch_size=2)
    b.add({"e":1})
    b.add({"e":2})
    batch = b.flush()
    assert batch == [{"e":1},{"e":2}]
    assert b.flush() == []
