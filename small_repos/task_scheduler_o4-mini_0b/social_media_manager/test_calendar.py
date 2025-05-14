import datetime
from postscheduler.calendar import configure_calendar_exclusions

def test_weekday_allowed():
    fn = configure_calendar_exclusions([])
    d = datetime.date(2023, 9, 20)  # Wednesday
    assert fn(d)

def test_weekend_blocked():
    fn = configure_calendar_exclusions([])
    d = datetime.date(2023, 9, 23)  # Saturday
    assert not fn(d)

def test_holiday_blocked():
    fn = configure_calendar_exclusions(["2023-09-20"])
    d = datetime.date(2023, 9, 20)
    assert not fn(d)
