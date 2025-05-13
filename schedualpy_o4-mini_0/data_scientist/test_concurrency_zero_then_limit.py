from scheduler import Scheduler, Task

def test_zero_then_update_limit():
    order = []
    def w1():
        order.append(1)
    def w2():
        order.append(2)
    sched = Scheduler()
    sched.set_concurrency_limit('g', 0)
    t1 = Task('a', w1, concurrency_group='g')
    sched.add_task(t1)
    sched.run()
    # nothing ran
    assert order == []
    # now raise limit
    sched.set_concurrency_limit('g', 1)
    sched.run()
    assert order == [1]
