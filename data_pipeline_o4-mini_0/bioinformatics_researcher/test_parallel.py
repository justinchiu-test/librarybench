from pipeline.parallel import ParallelExecutor

def test_parallel_executor():
    items = [1, 2, 3, 4]
    def square(x):
        return x * x
    executor = ParallelExecutor(max_workers=2)
    results = executor.map(square, items)
    assert results == [1, 4, 9, 16]
