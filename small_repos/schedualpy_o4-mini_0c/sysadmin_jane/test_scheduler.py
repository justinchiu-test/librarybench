import pytest
import time
import datetime
from scheduler import ThreadSafeScheduler

def test_enable_dst():
    sched = ThreadSafeScheduler()
    assert not sched.dst_enabled
    sched.enable_daylight_saving_support()
    assert sched.dst_enabled

def test_interval_job_execution():
    sched = ThreadSafeScheduler()
    flag = {'count': 0}
    def job():
        flag['count'] += 1
    sched.start()
    job_id = sched.schedule_interval(job, 1)
    time.sleep(1.5)
    sched.shutdown()
    assert flag['count'] >= 1

def test_one_off_task():
    sched = ThreadSafeScheduler()
    flag = {'done': False}
    def job():
        flag['done'] = True
    sched.start()
    sched.schedule_one_off_task(job, delay=1)
    time.sleep(1.5)
    sched.shutdown()
    assert flag['done']

def test_dynamic_reschedule():
    sched = ThreadSafeScheduler()
    def job(): pass
    job_id = sched.schedule_interval(job, 5)
    assert sched.jobs[job_id].schedule_params['interval'] == 5
    sched.dynamic_reschedule(job_id, interval=2)
    assert sched.jobs[job_id].schedule_params['interval'] == 2

def test_hooks_called():
    sched = ThreadSafeScheduler()
    calls = {'pre': 0, 'post': 0}
    def job(): pass
    def pre(jid):
        calls['pre'] += 1
    def post(jid):
        calls['post'] += 1
    sched.register_pre_hook(pre)
    sched.register_post_hook(post)
    sched.start()
    sched.schedule_one_off_task(job, delay=0.5)
    time.sleep(1)
    sched.shutdown()
    assert calls['pre'] == 1
    assert calls['post'] == 1

def test_jitter_and_drift():
    sched = ThreadSafeScheduler()
    sched.apply_jitter_and_drift_correction(jitter_seconds=0.5)
    def job(): pass
    job_id = sched.schedule_interval(job, 1)
    original_next = sched.jobs[job_id].next_run
    time.sleep(0.1)
    # let it run once
    sched.start()
    time.sleep(1.5)
    sched.shutdown()
    new_next = sched.jobs.get(job_id, None)
    # After first run, since it's interval, job still exists
    assert new_next is None or isinstance(new_next.next_run, float)

def test_task_group_pause():
    sched = ThreadSafeScheduler()
    def job(): pass
    j1 = sched.schedule_interval(job, 10)
    j2 = sched.schedule_interval(job, 10)
    sched.create_task_group('grp', [j1, j2])
    sched.pause_group('grp')
    assert j1 not in sched.jobs
    assert j2 not in sched.jobs

def test_load_plugin():
    sched = ThreadSafeScheduler()
    assert sched.load_plugin('plugin_test')
    assert hasattr(sched, 'plugin_loaded') and sched.plugin_loaded

