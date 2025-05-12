import pytest
from pipeline.pipeline import DataPipeline
from pipeline.errors import UnrecoverableError
from pipeline.metrics import create_counter

def test_run_success():
    dp = DataPipeline()
    assert dp.run() == "running"
    assert dp.counter_processed.get_count() == 1

def test_run_skip_on_error():
    dp = DataPipeline()
    dp.set_skip_on_error(True)
    dp._process = lambda: (_ for _ in ()).throw(Exception("fail"))
    # counters start at 0
    assert dp.run() == "running"
    assert dp.counter_failed.get_count() == 1

def test_run_halt_on_unrecoverable():
    dp = DataPipeline()
    dp._process = lambda: (_ for _ in ()).throw(UnrecoverableError("hard"))
    with pytest.raises(UnrecoverableError):
        dp.run()
