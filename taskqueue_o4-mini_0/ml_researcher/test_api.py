import pytest
from scheduler.api import RestAPI
from scheduler.auth import RoleBasedAccessControl
from scheduler.control import ConcurrencyControl
from scheduler.backends import LocalRunner

def setup_api():
    auth = RoleBasedAccessControl()
    auth.add_role('user',['enqueue','status'])
    auth.add_role('admin',['enqueue','status','cancel','reprioritize'])
    auth.assign_role('u1','user')
    auth.assign_role('a1','admin')
    control = ConcurrencyControl(max_global=1)
    backend = LocalRunner()
    api = RestAPI(control, backend, None, auth)
    return api

def test_enqueue_and_status():
    api = setup_api()
    run_id = api.enqueue_run('u1','g1', {'x':1})
    assert run_id.startswith('run-')
    status = api.get_status('u1', run_id)
    assert status == 'running'

def test_enqueue_no_perm():
    api = setup_api()
    with pytest.raises(PermissionError):
        api.enqueue_run('invalid','g1',{})

def test_cancel_and_metrics_and_release():
    api = setup_api()
    run_id = api.enqueue_run('u1','g1', {})
    with pytest.raises(PermissionError):
        api.cancel_run('u1', run_id)
    run_id2 = api.enqueue_run('a1','g2', {})
    res = api.cancel_run('a1', run_id2)
    assert res
    status = api.get_status('a1', run_id2)
    assert status == 'cancelled'
    run_id3 = api.enqueue_run('a1','g2', {})
    assert run_id3

def test_reprioritize():
    api = setup_api()
    run_id = api.enqueue_run('a1','g1', {})
    res = api.reprioritize_run('a1', run_id, 10)
    assert res
    run_id2 = api.enqueue_run('u1','g2', {})
    with pytest.raises(PermissionError):
        api.reprioritize_run('u1', run_id2, 5)
