import datetime
from datetime import timedelta
from scheduler.utils import next_run_cron

def test_next_run_cron_without_jitter():
    base = datetime.datetime(2020, 1, 1, 0, 0)
    cron = "0 0 * * *"  # daily at midnight
    next_run = next_run_cron(cron, base_time=base, jitter_seconds=0)
    assert isinstance(next_run, datetime.datetime)
    assert next_run == datetime.datetime(2020, 1, 2, 0, 0)

def test_next_run_cron_with_jitter(monkeypatch):
    base = datetime.datetime(2020, 1, 1, 0, 0)
    cron = "0 0 * * *"
    import random
    monkeypatch.setattr(random, 'uniform', lambda a, b: 60)
    next_run = next_run_cron(cron, base_time=base, jitter_seconds=60)
    assert next_run == datetime.datetime(2020, 1, 2, 0, 0) + timedelta(seconds=60)
