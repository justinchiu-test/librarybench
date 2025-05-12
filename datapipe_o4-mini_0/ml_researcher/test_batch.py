import pytest
from feature_pipeline.batch import run_batch

def test_run_batch_without_notifier():
    data = [1, 2, 3]
    processor = lambda x: x * 2
    results = run_batch(data, processor)
    assert results == [2, 4, 6]

def test_run_batch_with_notifier():
    data = [1, 2]
    processor = lambda x: x + 1
    calls = []
    def notifier(count, results):
        calls.append((count, results))
    results = run_batch(data, processor, notifier)
    assert results == [2, 3]
    assert calls == [(2, [2, 3])]
