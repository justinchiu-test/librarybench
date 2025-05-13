import threading
import time
from scheduler import ThreadSafeScheduler

def test_concurrent_schedule_and_cancel():
    scheduler = ThreadSafeScheduler()
    def add_and_remove(i):
        scheduler.schedule(f"t{i}", lambda: None, cron_expr=1)
        scheduler.cancel(f"t{i}")
    threads = []
    for i in range(20):
        t = threading.Thread(target=add_and_remove, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # no tasks should remain
    assert scheduler.tasks == {}
