import time
from Software_Developer.task_manager.scheduler import Scheduler

def test_schedule_interval():
    s = Scheduler()
    ctr = {"n":0}
    s.schedule(0.2, lambda: ctr.__setitem__("n", ctr["n"]+1))
    time.sleep(0.7)
    s.stop()
    # Should have fired at least 3 times: ~0.2,0.4,0.6
    assert ctr["n"] >= 3
