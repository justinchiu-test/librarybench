import datetime
import pytest
from pipeline.batching import BuiltInBatch

def test_size_batching():
    recs = list(range(7))
    batcher = BuiltInBatch(size=3)
    batches = batcher.batch(recs)
    assert batches == [list(range(3)), list(range(3,6)), [6]]

def test_time_batching():
    base = datetime.datetime.now()
    recs = [
        {"timestamp": base},
        {"timestamp": base + datetime.timedelta(seconds=2)},
        {"timestamp": base + datetime.timedelta(seconds=5)},
        {"timestamp": base + datetime.timedelta(seconds=12)}
    ]
    batcher = BuiltInBatch(time_window=5)
    batches = batcher.batch(recs)
    # first three within 5s, then new batch
    assert len(batches) == 2
    assert len(batches[0]) == 3
    assert len(batches[1]) == 1

def test_time_batching_missing_timestamp():
    batcher = BuiltInBatch(time_window=1)
    with pytest.raises(ValueError):
        batcher.batch([{"no_ts": 1}])
