import time
from collections import defaultdict

class RetentionPolicy:
    def __init__(self, tsdb, retention_map=None):
        self.tsdb = tsdb
        # retention_map: list of (age_limit_seconds, policy)
        # policy: 'keep', 'downsample', 'delete'
        # If not provided, we keep all data by default
        if retention_map is None:
            retention_map = [
                (float('inf'), 'keep')
            ]
        self.map = retention_map

    def enforce(self):
        now = time.time()
        new_storage = {}
        for series_key, points in self.tsdb.storage.items():
            kept = []
            # sort points
            points = sorted(points, key=lambda x: x[0])
            # classify points by age
            buckets = {'keep': [], 'downsample': [], 'delete': []}
            for ts, val in points:
                age = now - ts
                for limit, policy in self.map:
                    if age <= limit:
                        buckets[policy].append((ts, val))
                        break
            # keep
            kept.extend(buckets['keep'])
            # downsample: average per hour (3600)
            if buckets['downsample']:
                by_hour = defaultdict(list)
                for ts, val in buckets['downsample']:
                    hour = int(ts // 3600)
                    by_hour[hour].append(val)
                for hour, vals in by_hour.items():
                    t = hour * 3600
                    avg = sum(vals) / len(vals)
                    kept.append((t, avg))
            # delete: drop these
            if kept:
                new_storage[series_key] = kept
        self.tsdb.storage = new_storage
