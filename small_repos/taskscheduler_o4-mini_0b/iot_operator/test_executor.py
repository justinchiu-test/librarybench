import pytest
from iot_scheduler.executor import configure_executor

def test_threading_executor():
    ex = configure_executor('threading')
    fut = ex.submit(lambda x: x+1, 1)
    assert fut.result() == 2

def test_multiprocessing_executor():
    ex = configure_executor('multiprocessing')
    fut = ex.submit(lambda x: x*3, 2)
    assert fut.result() == 6

def test_unknown_mode():
    with pytest.raises(ValueError):
        configure_executor('unknown')
