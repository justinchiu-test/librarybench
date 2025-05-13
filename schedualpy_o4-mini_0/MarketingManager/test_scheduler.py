import pytest
import threading
import time
from scheduler import Scheduler, TaskStateError, DependencyError, TaskNotFoundError

def test_register_and_retrieve_task():
    sched = Scheduler()
    def dummy(): pass
    task = sched.register_task('t1', dummy, cron_expression='* * * * *', priority=5, timezone='UTC', one_off=False)
    assert 't1' in sched.tasks
    assert task.cron_expression == '* * * * *'
    assert task.priority == 5
    assert task.timezone == 'UTC'
    assert not task.one_off

def test_duplicate_registration():
    sched = Scheduler()
    sched.register_task('t1', lambda: None)
    with pytest.raises(TaskStateError):
        sched.register_task('t1', lambda: None)

def test_pre_post_hooks_order():
    sched = Scheduler()
    order = []
    def task_func():
        order.append('run')
    def pre_hook(task):
        order.append('pre')
    def post_hook(task):
        order.append('post')
    sched.register_task('t1', task_func)
    sched.register_pre_post_hooks('t1', pre_hooks=[pre_hook], post_hooks=[post_hook])
    sched.start_task('t1')
    assert order == ['pre', 'run', 'post']
    assert sched.tasks['t1'].state == 'completed'

def test_dependencies_enforced():
    sched = Scheduler()
    def f1(): pass
    def f2(): pass
    sched.register_task('t1', f1)
    sched.register_task('t2', f2, dependencies=['t1'])
    with pytest.raises(DependencyError):
        sched.start_task('t2')
    sched.start_task('t1')
    result = sched.start_task('t2')
    assert sched.tasks['t2'].state == 'completed'

def test_dependencies_dynamic_declare():
    sched = Scheduler()
    def f1(): pass
    def f2(): pass
    sched.register_task('t1', f1)
    sched.register_task('t2', f2)
    sched.declare_task_dependencies('t2', ['t1'])
    with pytest.raises(DependencyError):
        sched.start_task('t2')
    sched.start_task('t1')
    sched.start_task('t2')
    assert sched.tasks['t2'].state == 'completed'

def test_priority_sorting():
    sched = Scheduler()
    sched.register_task('low', lambda: None, priority=1)
    sched.register_task('high', lambda: None, priority=10)
    ordered = sched.tasks_by_priority()
    assert ordered[0].name == 'high'
    assert ordered[1].name == 'low'

def test_pause_resume_cancel_states():
    sched = Scheduler()
    # Test cancel before start
    sched.register_task('t1', lambda: None)
    sched.cancel_task('t1')
    assert sched.tasks['t1'].state == 'cancelled'
    with pytest.raises(TaskStateError):
        sched.start_task('t1')
    # Test pause/resume on invalid states
    sched.register_task('t2', lambda: None)
    with pytest.raises(TaskStateError):
        sched.pause_task('t2')
    with pytest.raises(TaskStateError):
        sched.resume_task('t2')

def test_dynamic_reschedule():
    sched = Scheduler()
    sched.register_task('t1', lambda: None, cron_expression='0 0 * * *')
    sched.dynamic_reschedule('t1', '30 1 * * *')
    assert sched.tasks['t1'].cron_expression == '30 1 * * *'
    with pytest.raises(TaskNotFoundError):
        sched.dynamic_reschedule('nope', '* * * * *')

def test_one_off_task_flag():
    sched = Scheduler()
    def f(): pass
    task = sched.register_task('t1', f, one_off=True)
    assert task.one_off
    # even if cron_expression is set, one_off remains
    sched.dynamic_reschedule('t1', '0 12 * * *')
    assert sched.tasks['t1'].one_off

def test_timezone_awareness():
    sched = Scheduler()
    def f(): pass
    task = sched.register_task('t1', f, timezone='Asia/Tokyo')
    assert task.timezone == 'Asia/Tokyo'

def test_task_not_found_errors():
    sched = Scheduler()
    with pytest.raises(TaskNotFoundError):
        sched.start_task('missing')
    with pytest.raises(TaskNotFoundError):
        sched.pause_task('missing')
    with pytest.raises(TaskNotFoundError):
        sched.register_pre_post_hooks('missing', pre_hooks=[])
    with pytest.raises(TaskNotFoundError):
        sched.set_task_priority('missing', 5)
    with pytest.raises(TaskNotFoundError):
        sched.declare_task_dependencies('missing', ['a'])
    with pytest.raises(TaskNotFoundError):
        sched.cancel_task('missing')
    with pytest.raises(TaskNotFoundError):
        sched.dynamic_reschedule('missing', '* * * * *')
