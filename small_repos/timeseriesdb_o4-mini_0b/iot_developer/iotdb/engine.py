import time
from .cache import QueryCache
from .wal import WriteAheadLog
from .snapshot import Snapshot
from .retention import apply_retention
from .interpolation import linear_interpolation, spline_interpolation
from .utils import tag_pattern_query, json_import

class IoTEngine:
    def __init__(self, wal_path=None, snapshot_path=None, cache_ttl=60):
        self.data = {}
        self.tags = {}
        self.transformations = []
        self.detectors = []
        self.replicas = []
        self.cache = QueryCache(cache_ttl)
        if wal_path:
            self.wal = WriteAheadLog(wal_path)
        else:
            self.wal = None
        if snapshot_path:
            self.snapshot = Snapshot(snapshot_path)
        else:
            self.snapshot = None

    def register_transformation(self, func):
        self.transformations.append(func)

    def register_detector(self, func):
        self.detectors.append(func)

    def replicate_to(self, other_engine):
        self.replicas.append(other_engine)

    def ingest(self, device_id, value, timestamp=None, tags=None):
        # Accept zero timestamps; only use now() if timestamp is None
        ts = timestamp if timestamp is not None else time.time()
        # Apply transformations and detectors
        for func in self.transformations:
            value = func(device_id, value, ts, tags)
        for func in self.detectors:
            func(device_id, value, ts, tags)
        # Store the reading
        self.data.setdefault(device_id, []).append((ts, value))
        if tags:
            self.tags[device_id] = tags
        # Write-ahead log
        if self.wal:
            self.wal.append({'device_id': device_id, 'timestamp': ts, 'value': value, 'tags': tags})
        # Replicate to other engines
        for replica in self.replicas:
            replica.ingest(device_id, value, ts, tags)

    def query(self, device_ids, start, end, use_cache=False):
        key = (tuple(device_ids), start, end)
        if use_cache:
            cached = self.cache.get(key)
            if cached is not None:
                return cached
        result = {}
        for dev in device_ids:
            readings = self.data.get(dev, [])
            res = [(ts, val) for ts, val in readings if start <= ts <= end]
            result[dev] = res
        if use_cache:
            self.cache.set(key, result)
        return result

    def snapshot_save(self):
        if self.snapshot:
            state = {'data': self.data, 'tags': self.tags}
            self.snapshot.save(state)

    def snapshot_load(self):
        if self.snapshot:
            state = self.snapshot.load()
            if state:
                self.data = state['data']
                self.tags = state['tags']

    def import_json(self, path):
        records = json_import(path)
        for rec in records:
            self.ingest(rec['device_id'], rec['value'], rec.get('timestamp'), rec.get('tags'))

    def query_by_tag(self, pattern, start, end):
        devs = tag_pattern_query(self.tags, pattern)
        return self.query(devs, start, end)

    def apply_retention(self, now=None):
        self.data = apply_retention(self.data, now)

    def interpolate(self, device_id, timestamp, method='linear'):
        readings = sorted(self.data.get(device_id, []), key=lambda x: x[0])
        if method == 'linear':
            return linear_interpolation(readings, timestamp)
        else:
            return spline_interpolation(readings, timestamp)
