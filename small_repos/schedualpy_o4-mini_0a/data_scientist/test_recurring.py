from scheduler import Scheduler, Task

def test_recurring_task():
    count = {'n': 0}
    def work():
        count['n'] += 1
    sched = Scheduler()
    t = Task('r', work).set_recurring()
    sched.add_task(t)
    # run twice
    sched.run()
    sched.run()
    assert count['n'] >= 2
