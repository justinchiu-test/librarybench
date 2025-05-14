from scheduler import Scheduler, Task

def test_workflow_chaining_and_conditional():
    order = []
    def t1f():
        order.append('t1')
        return 5
    def t2f():
        order.append('t2')
    def t3f():
        order.append('t3')
    sched = Scheduler()
    t1 = Task('t1', t1f)
    t2 = Task('t2', t2f)
    t3 = Task('t3', t3f)
    t1.then(t2)
    t1.then_if(lambda x: x > 3, t3)
    sched.add_task(t1)
    sched.run()
    assert order == ['t1', 't2', 't3']
