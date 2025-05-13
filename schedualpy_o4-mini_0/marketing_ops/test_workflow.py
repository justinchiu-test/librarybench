import datetime
from scheduler.scheduler import Scheduler, Task

def test_workflow_chaining():
    sched = Scheduler()
    executed = []
    def action1(ctx):
        executed.append('first')
    def action2(ctx):
        executed.append('second')
    t1 = Task(name="t1", action=action1, schedule=datetime.datetime.now(), delay=0)
    t2 = Task(name="t2", action=action2)
    t1.add_chain(t2)
    sched.register_task(t1)
    sched.run_pending()
    sched.run_pending()
    assert executed == ['first', 'second']
