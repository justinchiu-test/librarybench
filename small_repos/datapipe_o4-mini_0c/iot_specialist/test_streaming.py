from telemetry.streaming import run_streaming

def test_run_streaming():
    source = [1,2,3]
    def proc(x): return x*2
    out = run_streaming(source, proc)
    assert out == [2,4,6]
