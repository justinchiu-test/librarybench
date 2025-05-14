import time
from collections import defaultdict

def apply_retention(data, now=None):
    if now is None:
        now = time.time()
    raw_limit = now - 14*24*3600
    agg_limit = now - 90*24*3600
    new_data = {}
    for device, readings in data.items():
        agg_buckets = defaultdict(list)
        filtered = []
        for ts, value in readings:
            if ts < agg_limit:
                continue
            if ts < raw_limit:
                bucket = int(ts // 3600 * 3600)
                agg_buckets[bucket].append(value)
            else:
                filtered.append((ts, value))
        for bucket, values in agg_buckets.items():
            if values:
                if isinstance(values[0], dict):
                    avg = {}
                    keys = values[0].keys()
                    for k in keys:
                        avg[k] = sum(v[k] for v in values)/len(values)
                else:
                    avg = sum(values)/len(values)
                filtered.append((bucket, avg))
        filtered.sort(key=lambda x: x[0])
        new_data[device] = filtered
    return new_data
