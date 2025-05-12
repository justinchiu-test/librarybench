import time
from pipeline.streaming import StreamingRunner

def test_streaming_runner():
    seq = []
    runner = None
    def process():
        seq.append('x')
        if len(seq) >= 3:
            runner.stop()
    runner = StreamingRunner(process)
    runner.start()
    time.sleep(1)
    assert len(seq) >= 3
    assert not runner.running
