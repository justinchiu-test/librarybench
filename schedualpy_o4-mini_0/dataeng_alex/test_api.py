import pytest
from scheduler import ThreadSafeScheduler
from api import RESTfulManagementAPI
from datetime import datetime, timedelta

def test_api_add_remove_list():
    scheduler = ThreadSafeScheduler()
    api = RESTfulManagementAPI(scheduler)
    def f(): pass
    api.add_job('a1', 1, func=f)
    assert 'a1' in scheduler.tasks
    resp = api.list_jobs()
    assert 'a1' in resp['jobs']
    api.remove_job('a1')
    assert 'a1' not in scheduler.tasks

def test_api_reschedule_and_one_off():
    scheduler = ThreadSafeScheduler()
    api = RESTfulManagementAPI(scheduler)
    def f(): pass
    api.add_job('b1', 1, func=f)
    api.reschedule_job('b1', 5)
    assert scheduler.tasks['b1'].cron_expr == 5
    run_at = datetime.now() + timedelta(seconds=1)
    api.run_one_off('b2', run_at, func=f)
    assert 'b2' in scheduler.tasks
