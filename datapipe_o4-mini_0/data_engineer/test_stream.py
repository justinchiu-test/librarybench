from pipeline.stream import run_streaming

def test_run_streaming_all_success():
    def gen():
        for i in [1, 2, 3]:
            yield i
    def proc(x):
        pass
    metrics = run_streaming(gen(), proc)
    assert metrics == {'processed': 3, 'succeeded': 3, 'failed': 0}

def test_run_streaming_with_failures_and_max():
    def gen():
        for i in range(5):
            yield i
    def proc(x):
        if x % 2 == 0:
            raise Exception
    metrics = run_streaming(gen(), proc, max_events=3)
    assert metrics == {'processed': 3, 'succeeded': 1, 'failed': 2}
