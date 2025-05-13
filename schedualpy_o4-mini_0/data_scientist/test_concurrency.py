from scheduler import Scheduler, Task

def test_concurrency_limit_blocks():
    order = []
    def work1():
        order.append('w1')
    def work2():
        order.append('w2')
    sched = Scheduler()
    sched.set_concurrency_limit('grp', 0)
    t1 = Task('t1', work1, concurrency_group='grp')
    t2 = Task('t2', work2, concurrency_group='grp')
    sched.add_task(t1)
    sched.add_task(t2)
    sched.run()
    # With limit 0, no task should run
    assert order == []
    # Queue should still contain both
    assert len(Scheduler.shared_queue) == 2
