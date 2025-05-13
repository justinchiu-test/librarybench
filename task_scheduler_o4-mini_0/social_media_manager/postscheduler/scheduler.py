def schedule_daily(channels_times):
    """
    channels_times: dict of channel -> list of "HH:MM" strings
    returns list of job dicts
    """
    jobs = []
    for channel, times in channels_times.items():
        for t in times:
            jobs.append({"channel": channel, "time": t})
    return jobs

def schedule_cron(expr, task_name):
    """
    expr: cron expression string
    task_name: name of task
    returns dict representing the cron job
    """
    return {"cron": expr, "task": task_name}
