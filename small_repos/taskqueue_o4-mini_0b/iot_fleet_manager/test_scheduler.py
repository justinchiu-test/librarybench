import time
from iot.scheduler import DelayedScheduler

def test_schedule_zero_delay():
    executed = []
    def task():
        executed.append(True)
    sched = DelayedScheduler()
    sched.schedule("t1", task, 0)
    time.sleep(0.1)
    assert executed == [True]
    assert sched.scheduled[0][0] == "t1"

def test_schedule_wave():
    executed = []
    def make_task(i):
        return lambda: executed.append(i)
    tasks = [(f"id{i}", make_task(i)) for i in range(3)]
    sched = DelayedScheduler()
    sched.schedule_wave(tasks, 0)
    time.sleep(0.1)
    assert set(executed) == {0,1,2}
    assert len(sched.scheduled) == 3
