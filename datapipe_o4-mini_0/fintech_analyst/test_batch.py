import logging
from batch import run_batch

def test_run_batch(caplog):
    caplog.set_level(logging.INFO)
    trades = [1, 2, 3]
    def process(x):
        return x + 10
    results = run_batch(trades, process)
    assert results == [11, 12, 13]
    assert "Batch processing started" in caplog.text
    assert "Batch processing completed" in caplog.text
