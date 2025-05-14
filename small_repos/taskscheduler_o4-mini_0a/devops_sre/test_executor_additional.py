# ensure square is picklable for process executor
from scheduler.executor import Executor

def square(x):
    return x * x

def test_process_executor_square():
    executor = Executor(mode='process')
    future = executor.submit(square, 4)
    assert future.result() == 16
    executor.shutdown()
