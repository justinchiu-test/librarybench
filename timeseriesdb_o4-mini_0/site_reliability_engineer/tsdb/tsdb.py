import os
import time
import math
from tsdb.query_cache import QueryCache
from tsdb.wal import WriteAheadLog
from tsdb.snapshot import PersistenceSnapshot
from tsdb.anomaly import AnomalyDetector
from tsdb.json_import import JSONImport
from tsdb.cluster import ClusterReplication
from tsdb.tag_pattern import TagPatternQuery
from tsdb.retention import RetentionPolicy
from tsdb.transform import TransformationHook
from tsdb.interpolation import Interpolation

class TimeSeriesDB:
    def __init__(self, wal_path='wal.log', snapshot_path='snapshot.pkl', cache_ttl=60, retention_map=None):
        self.storage = {}  # key -> list of (timestamp, value); key: (name, tags_tuple)
        self.wal = WriteAheadLog(wal_path)
        self.snapshot = PersistenceSnapshot(snapshot_path, self)
        self.cache = QueryCache(cache_ttl)
        self.anomaly = AnomalyDetector()
        self.transform = TransformationHook()
        self.cluster = ClusterReplication()
        self.retention = RetentionPolicy(self, retention_map)
        self.importer = JSONImport(self)
        # load snapshot
        self.snapshot.load()
        # replay WAL
        for rec in self.wal.replay():
            self._insert_internal(rec, replicate=False, wal_write=False)

    def _make_key(self, record):
        name = record.get('name')
        tags = record.get('tags') or {}
        # key as (name, frozenset of items) to allow dict keys
        return (name, frozenset(tags.items()))

    def insert(self, record, replicate=True, wal_write=True):
        self._insert_internal(record, replicate, wal_write)

    def _insert_internal(self, record, replicate=True, wal_write=True):
        record = self.transform.apply(record)
        key = self._make_key(record)
        lst = self.storage.setdefault(key, [])
        lst.append((record['timestamp'], record['value']))
        if wal_write:
            self.wal.append(record)
        # invalidate cache
        self.cache.invalidate()
        # anomaly
        self.anomaly.run(record)
        # replicate
        if replicate:
            self.cluster.replicate(record)
        # retention
        self.retention.enforce()

    def query(self, name, start, end, agg=None):
        """
        Query values for series 'name' between start and end inclusive.
        If agg is None: return list of values (deduplicated by timestamp in ascending order).
        If agg == 'sum', 'avg', or 'p95': return aggregated value.
        """
        cache_key = (name, start, end, agg)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        # collect all matching (timestamp, value)
        points = []
        for (n, tags), pts in self.storage.items():
            if n != name:
                continue
            for ts, v in pts:
                if start <= ts <= end:
                    points.append((ts, v))

        # sort by timestamp
        points.sort(key=lambda x: x[0])
        # deduplicate by timestamp
        seen_ts = set()
        vals = []
        for ts, v in points:
            if ts in seen_ts:
                continue
            seen_ts.add(ts)
            vals.append(v)

        # compute result
        if agg is None:
            result = vals
        elif agg == 'sum':
            result = sum(vals)
        elif agg == 'avg':
            result = sum(vals) / len(vals) if vals else None
        elif agg == 'p95':
            if not vals:
                result = None
            else:
                sorted_vals = sorted(vals)
                n = len(sorted_vals)
                # compute 95th percentile: use ceil to choose the index
                idx = math.ceil(0.95 * n) - 1
                # clamp index
                idx = max(0, min(idx, n - 1))
                result = sorted_vals[idx]
        else:
            result = vals

        # cache and return
        self.cache.set(cache_key, result)
        return result

    def register_anomaly_hook(self, func):
        self.anomaly.register(func)

    def register_transform_hook(self, func):
        self.transform.register(func)

    def add_cluster_peer(self, peer):
        self.cluster.register(peer)

    def import_json(self, path):
        self.importer.import_file(path)

    def query_tags(self, pattern):
        return TagPatternQuery.query(self, pattern)

    def interpolate(self, series_key, start, end, interval, method='linear'):
        points = self.storage.get(series_key, [])
        if method == 'linear':
            return Interpolation.linear(points, start, end, interval)
        else:
            return Interpolation.step(points, start, end, interval)

    def snapshot_now(self):
        self.snapshot.snapshot()
