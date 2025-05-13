import time
import threading
from datetime import datetime, timedelta
import pytest
from scheduler import ThreadSafeScheduler

def test_schedule_and_run_one_off():
    scheduler = ThreadSafeScheduler()
    results = []
    run_time = datetime.now() + timedelta(seconds=1)
    scheduler.schedule_one_off('job1', lambda: results.append('ran'), run_time)
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert 'ran' in results

def test_recurring_schedule_and_reschedule():
    scheduler = ThreadSafeScheduler()
    counter = {'count': 0}
    scheduler.schedule('job2', lambda: counter.__setitem__('count', counter['count']+1), cron_expr=1)
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert counter['count'] == 1
    scheduler.reschedule('job2', 2)
    time.sleep(2.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert counter['count'] == 2

def test_cancel():
    scheduler = ThreadSafeScheduler()
    counter = {'c': 0}
    scheduler.schedule('job3', lambda: counter.__setitem__('c', counter['c']+1), cron_expr=1)
    scheduler.cancel('job3')
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert counter['c'] == 0

def test_hooks():
    scheduler = ThreadSafeScheduler()
    order = []
    def pre(tid): order.append(f"pre-{tid}")
    def post(tid): order.append(f"post-{tid}")
    scheduler.schedule('job4', lambda: order.append('run'), cron_expr=1)
    scheduler.register_pre_hook('job4', pre)
    scheduler.register_post_hook('job4', post)
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert order == ['pre-job4','run','post-job4']

def test_jitter_effect():
    scheduler = ThreadSafeScheduler()
    # fix random
    import random
    random.seed(0)
    call_times = []
    scheduler.schedule('job5', lambda: call_times.append(datetime.now()), cron_expr=1, jitter_seconds=0.5)
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert len(call_times) == 1

def test_task_group_pause_resume():
    scheduler = ThreadSafeScheduler()
    scheduler.create_task_group('grp')
    results = []
    scheduler.schedule('job6', lambda: results.append(1), cron_expr=1, group='grp')
    scheduler.pause_group('grp')
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert results == []
    scheduler.resume_group('grp')
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    assert results == [1]

def test_timezone_setting():
    scheduler = ThreadSafeScheduler()
    scheduler.schedule('job7', lambda: None, cron_expr=10, tz='UTC')
    task = scheduler.tasks['job7']
    assert task.tz == 'UTC'
