import datetime

def configure_calendar_exclusions(blackout_dates=None):
    """
    blackout_dates: list of 'YYYY-MM-DD' strings
    returns a function that given a date returns True if allowed
    """
    blackout = set(blackout_dates or [])
    def is_allowed(date):
        # date: datetime.date
        if date.weekday() >= 5:
            return False
        if date.isoformat() in blackout:
            return False
        return True
    return is_allowed
