import pytest
import time
import urllib.request
from scheduler import Scheduler

def test_run_coroutine_single():
    scheduler = Scheduler()
    async def sample():
        return "result"
    res = scheduler.run_coroutine(sample())
    assert res == "result"

def test_run_coroutine_multiple():
    scheduler = Scheduler()
    async def sample(i):
        return i * 2
    res = scheduler.run_coroutine(sample(2), sample(3))
    assert isinstance(res, list)
    assert sorted(res) == [4, 6]

def test_register_error_handler():
    scheduler = Scheduler()
    def handler(err):
        return "handled"
    scheduler.register_error_handler("stage1", handler)
    assert "stage1" in scheduler.error_handlers
    assert scheduler.error_handlers["stage1"] is handler

def test_schedule_daily_and_cron():
    scheduler = Scheduler()
    scheduler.schedule_daily("qc_check", "02:00")
    assert scheduler.daily_schedules["qc_check"] == "02:00"
    scheduler.schedule_cron("weekly_cleanup", "0 3 * * 0")
    assert scheduler.cron_schedules["weekly_cleanup"] == "0 3 * * 0"

def test_send_notification_and_tags():
    scheduler = Scheduler()
    scheduler.send_notification("Job failed", level="error")
    assert scheduler.notifications[-1] == {"message": "Job failed", "level": "error"}
    scheduler.add_tag("align_task", "alignment")
    assert scheduler.tags["align_task"] == "alignment"

def test_define_dependency_and_exclusions():
    scheduler = Scheduler()
    scheduler.define_dependency("annotation", "variant_call")
    assert "annotation" in scheduler.dependencies
    assert "variant_call" in scheduler.dependencies["annotation"]
    scheduler.configure_calendar_exclusions(["2023-12-25", "2024-01-01"])
    assert "2023-12-25" in scheduler.exclusions
    assert "2024-01-01" in scheduler.exclusions

def test_expose_metrics():
    scheduler = Scheduler()
    metrics = scheduler.expose_metrics()
    assert "job_duration" in metrics
    assert "queue_length" in metrics
    assert "error_count" in metrics
    assert isinstance(metrics["job_duration"], list)

def test_health_check():
    scheduler = Scheduler()
    host, port = scheduler.start_health_check(host="127.0.0.1", port=0)
    time.sleep(0.1)
    url = f"http://{host}:{port}/health"
    resp = urllib.request.urlopen(url)
    assert resp.status == 200
    body = resp.read()
    assert body == b"OK"
    scheduler._health_server.shutdown()
