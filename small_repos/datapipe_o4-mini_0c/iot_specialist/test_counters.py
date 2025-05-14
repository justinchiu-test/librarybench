import threading
from telemetry.counters import counter_manager

def test_single_thread():
    counter_manager.increment_counter("sensorA", parsed=True)
    counter_manager.increment_counter("sensorA", parsed=False)
    counts = counter_manager.get_counts("sensorA")
    assert counts['total'] >= 2
    assert counts['parsed'] >= 1
    assert counts['dropped'] >= 1

def test_thread_safety():
    def worker():
        for _ in range(1000):
            counter_manager.increment_counter("sensorB", parsed=True)
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    counts = counter_manager.get_counts("sensorB")
    assert counts['total'] == 5000
    assert counts['parsed'] == 5000
    assert counts['dropped'] == 0
