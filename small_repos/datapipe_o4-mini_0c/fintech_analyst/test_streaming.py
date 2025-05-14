from streaming import run_streaming

def test_run_streaming():
    source = [1, 2, 3]
    collected = []
    def process(x):
        collected.append(x*10)
    run_streaming(source, process)
    assert collected == [10, 20, 30]
