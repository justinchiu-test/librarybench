import time
from task_queue.scheduler import Scheduler

def test_scheduler():
    s = Scheduler()
    now = time.time()
    s.schedule('t1', now + 0.1)
    s.schedule('t2', now + 1)
    ready = s.get_ready(now)
    assert ready == []
    ready = s.get_ready(now + 0.2)
    assert 't1' in ready
    assert 't2' not in ready
