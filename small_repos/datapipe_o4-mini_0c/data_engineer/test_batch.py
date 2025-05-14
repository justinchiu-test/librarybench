import pytest
from pipeline.batch import run_batch

def test_run_batch_all_success(capsys):
    records = [1, 2, 3]
    def f(x):
        print(x)
    metrics = run_batch(f, records)
    captured = capsys.readouterr()
    assert "Batch started" in captured.out
    assert "Batch ended" in captured.out
    assert metrics == {'processed': 3, 'succeeded': 3, 'failed': 0}

def test_run_batch_with_failures():
    records = [1, 0, 2]
    def f(x):
        if x == 0:
            raise Exception("fail")
    metrics = run_batch(f, records)
    assert metrics == {'processed': 3, 'succeeded': 2, 'failed': 1}
