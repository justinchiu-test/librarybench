import pytest
import threading
from scheduler import Scheduler

def test_concurrent_registration():
    sched = Scheduler()
    errors = []
    def register(name):
        try:
            sched.register_task(name, lambda: None)
        except Exception as e:
            errors.append(e)
    threads = [threading.Thread(target=register, args=(f't{i}',)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(sched.tasks) == 50
    assert not errors

def test_concurrent_state_changes():
    sched = Scheduler()
    sched.register_task('t1', lambda: None)
    # cancel in one thread while starting in another
    results = {'started': False, 'cancelled': False}
    def start_task():
        try:
            sched.start_task('t1')
            results['started'] = True
        except:
            results['started'] = False
    def cancel_task():
        try:
            sched.cancel_task('t1')
            results['cancelled'] = True
        except:
            results['cancelled'] = False
    t1 = threading.Thread(target=start_task)
    t2 = threading.Thread(target=cancel_task)
    t2.start()
    t1.start()
    t1.join()
    t2.join()
    # Only one should succeed, cannot both start and cancel
    assert results['started'] != results['cancelled']
