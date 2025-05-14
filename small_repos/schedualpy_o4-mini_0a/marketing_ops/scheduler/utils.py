import datetime
import random

def next_run_cron(cron_expr, base_time=None, jitter_seconds=0):
    """
    Compute next run datetime based on a simple cron expression (minute and hour),
    with optional jitter. Supports expressions like "M H * * *". Other fields are ignored.
    """
    base = base_time or datetime.datetime.now()
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_expr}")
    minute, hour, _, _, _ = parts

    # Determine next occurrence
    try:
        if minute != '*' and hour != '*':
            target_minute = int(minute)
            target_hour = int(hour)
            # build candidate
            next_time = base.replace(hour=target_hour,
                                     minute=target_minute,
                                     second=0,
                                     microsecond=0)
            # if it's not strictly in the future, move one day ahead
            if next_time <= base:
                next_time += datetime.timedelta(days=1)
        else:
            # fallback: every minute
            next_time = base + datetime.timedelta(minutes=1)
    except Exception:
        # fallback in case of any parsing issues
        next_time = base + datetime.timedelta(minutes=1)

    if jitter_seconds:
        offset = random.uniform(-jitter_seconds, jitter_seconds)
        next_time += datetime.timedelta(seconds=offset)

    return next_time
