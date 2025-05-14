import datetime
from scheduler.scheduler import Scheduler, Task

def test_pre_and_post_hooks():
    sched = Scheduler()
    log = []
    def action(ctx):
        log.append('action')
    def pre(ctx):
        log.append('pre')
    def post(ctx):
        log.append('post')
    t = Task(name="h", action=action, schedule=datetime.datetime.now(), pre_hooks=[pre], post_hooks=[post])
    sched.register_task(t)
    sched.run_pending()
    assert log == ['pre', 'action', 'post']
