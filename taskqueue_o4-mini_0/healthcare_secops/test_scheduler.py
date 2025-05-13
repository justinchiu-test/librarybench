import pytest
from datetime import datetime
from pipeline.scheduler import DelayedTaskScheduling

def test_schedule_off_peak():
    sched = DelayedTaskScheduling()
    dt = datetime(2021,1,1,2,30)
    sched.schedule('task1', dt)
    assert sched.get_tasks()['task1'] == dt

def test_schedule_peak_hours():
    sched = DelayedTaskScheduling()
    dt = datetime(2021,1,1,8,0)
    with pytest.raises(ValueError):
        sched.schedule('task2', dt)
