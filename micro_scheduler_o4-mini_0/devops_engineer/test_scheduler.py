import pytest
from scheduler.scheduler import Scheduler

def test_scheduler_methods_exist():
    sched = Scheduler()
    for method in [
        'graceful_shutdown', 'health_check', 'trigger_job',
        'schedule_job', 'set_persistence_backend', 'exponential_backoff',
        'define_dependencies', 'retry_job', 'limit_resources'
    ]:
        assert hasattr(sched, method), f"Missing method {method}"

def test_schedule_and_trigger_job():
    sched = Scheduler()
    def sample():
        return "done"
    sched.schedule_job("job1", func=sample)
    assert "job1" in sched.jobs
    result = sched.trigger_job("job1")
    assert result == "done"

def test_trigger_nonexistent_job():
    sched = Scheduler()
    assert sched.trigger_job("nonexistent") is None

def test_health_check_returns_ok():
    sched = Scheduler()
    status = sched.health_check()
    assert status["status"] == "ok"
    assert isinstance(status["jobs"], list)

def test_schedule_job_params():
    sched = Scheduler()
    sched.schedule_job(
        "job2",
        func=lambda: None,
        delay=10,
        interval=5,
        cron="* * * * *",
        timezone="UTC"
    )
    job = sched.jobs["job2"]
    assert job["delay"] == 10
    assert job["interval"] == 5
    assert job["cron"] == "* * * * *"
    assert job["timezone"] == "UTC"

def test_set_persistence_backend():
    from scheduler.persistence import RedisBackend
    sched = Scheduler()
    backend = RedisBackend("redis://localhost")
    sched.set_persistence_backend(backend)
    assert sched.persistence is backend

def test_define_dependencies():
    sched = Scheduler()
    sched.define_dependencies("jobA", depends_on=["jobB"])
    assert sched.dependencies["jobA"] == ["jobB"]

def test_retry_job():
    sched = Scheduler()
    sched.schedule_job("job3", func=lambda: None)
    backoff_strategy = {'type': 'fixed', 'delay': 5}
    sched.retry_job("job3", retry_count=3, backoff=backoff_strategy)
    retry = sched.jobs["job3"]["retry"]
    assert retry["count"] == 3
    assert retry["backoff"] == backoff_strategy

def test_limit_resources():
    sched = Scheduler()
    sched.limit_resources("jobX", cpu=2, memory=512, io=100)
    limits = sched.resource_limits["jobX"]
    assert limits["cpu"] == 2
    assert limits["memory"] == 512
    assert limits["io"] == 100

def test_exponential_backoff():
    sched = Scheduler()
    backoff = sched.exponential_backoff(base=2, factor=3)
    assert backoff(1) == 2
    assert backoff(2) == 6
    assert backoff(3) == 18
