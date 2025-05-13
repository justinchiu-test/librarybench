import pytest
from scheduler import Scheduler, Task

def test_simple_task_execution():
    outputs = []
    def work():
        outputs.append('done')
        return 'ok'
    sched = Scheduler()
    t = Task('t1', work)
    sched.add_task(t)
    sched.run()
    assert outputs == ['done']

def test_task_return_value_and_retry():
    calls = {'count': 0}
    def flaky():
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError()
        return 'success'
    sched = Scheduler()
    t = Task('flaky', flaky, retries=1)
    results = []
    def post(task, result):
        results.append(result)
    sched.register_post_hook(post)
    sched.add_task(t)
    sched.run()
    assert results == ['success']
