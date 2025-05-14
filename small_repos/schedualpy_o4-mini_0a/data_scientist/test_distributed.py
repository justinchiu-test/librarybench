from scheduler import Scheduler, Task

def test_shared_queue_between_schedulers():
    results = []
    def work():
        results.append('x')
    s1 = Scheduler()
    s2 = Scheduler()
    t = Task('d', work)
    s1.add_task(t)
    # run with both schedulers
    s1.run()
    s2.run()
    assert results == ['x']
