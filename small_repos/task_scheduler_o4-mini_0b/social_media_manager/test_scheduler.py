from postscheduler.scheduler import schedule_daily, schedule_cron

def test_schedule_daily():
    cfg = {
        "twitter": ["09:00", "18:00"],
        "facebook": ["12:00"]
    }
    jobs = schedule_daily(cfg)
    assert {"channel": "twitter", "time": "09:00"} in jobs
    assert {"channel": "twitter", "time": "18:00"} in jobs
    assert {"channel": "facebook", "time": "12:00"} in jobs
    assert len(jobs) == 3

def test_schedule_cron():
    cron = "0 0 1 * *"
    task = "month_report"
    result = schedule_cron(cron, task)
    assert result["cron"] == cron
    assert result["task"] == task
