from collections import defaultdict
import datetime

def tumbling_window(events, window_size):
    """
    events: list of (timestamp ISO str, value)
    window_size: seconds
    returns dict mapping window start datetime to list of values
    """
    buckets = defaultdict(list)
    for ts_str, val in events:
        ts = datetime.datetime.fromisoformat(ts_str)
        # compute window start
        sec = (ts.minute * 60 + ts.second) // window_size * window_size
        start = ts.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=sec)
        buckets[start].append(val)
    return buckets

def sliding_window(values, size):
    """
    values: list
    size: window length
    returns list of lists
    """
    result = []
    for i in range(len(values) - size + 1):
        result.append(values[i:i+size])
    return result
