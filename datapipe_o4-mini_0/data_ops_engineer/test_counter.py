import threading
from pipeline.counter import create_counter
import pipeline.config as config

def test_create_and_use_counter():
    # create a counter
    c = create_counter("stage1")
    assert "stage1" in config.counters
    # single-thread increment
    c.inc()
    c.inc(4)
    assert c.get() == 5

def test_counter_thread_safety():
    c = create_counter("thread_stage")
    def worker():
        for _ in range(1000):
            c.inc()
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # 5 threads * 1000 increments each = 5000
    assert c.get() == 5000
