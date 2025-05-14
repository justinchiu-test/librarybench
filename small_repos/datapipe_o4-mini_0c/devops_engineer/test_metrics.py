import threading
from pipeline.metrics import Metrics

def test_increment_counter_thread_safety():
    m = Metrics()
    def worker():
        for _ in range(1000):
            m.increment_counter('stage1', 'success')
    threads = []
    for _ in range(5):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    counts = m.get_counts('stage1')
    assert counts['success'] == 5000
