import threading
import pytest
from feature_pipeline.counters import counter, IncrementCounter

def test_increment_and_get():
    cnt = IncrementCounter()
    assert cnt.get('test') == 0
    cnt.increment('test')
    assert cnt.get('test') == 1
    cnt.increment('test', 4)
    assert cnt.get('test') == 5

def test_thread_safety():
    cnt = IncrementCounter()
    def worker():
        for _ in range(1000):
            cnt.increment('t')

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert cnt.get('t') == 10000
