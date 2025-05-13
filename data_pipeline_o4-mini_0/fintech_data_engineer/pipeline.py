import json
import threading
import random
from collections import OrderedDict, defaultdict

class Stage:
    def process(self, record):
        raise NotImplementedError

class Pipeline:
    def __init__(self, stages=None):
        self.stages = stages or []

    def add_stage(self, stage):
        self.stages.append(stage)

    def run(self, records):
        outputs = []
        for record in records:
            r = record
            skip = False
            for stage in self.stages:
                try:
                    r = stage.process(r)
                    if r is None:
                        skip = True
                        break
                except Exception as e:
                    if hasattr(stage, 'handle_error'):
                        r = stage.handle_error(e, r)
                        if r is None:
                            skip = True
                            break
                    else:
                        raise
            if not skip:
                outputs.append(r)
        return outputs

class ErrorHandlingRetry(Stage):
    def __init__(self, inner_stage, retries=3):
        self.inner = inner_stage
        self.retries = retries

    def process(self, record):
        last_exc = None
        for attempt in range(self.retries):
            try:
                return self.inner.process(record)
            except Exception as e:
                last_exc = e
        raise last_exc

class ErrorHandlingFallback(Stage):
    def __init__(self, inner_stage, fallback_value):
        self.inner = inner_stage
        self.fallback = fallback_value

    def process(self, record):
        try:
            return self.inner.process(record)
        except Exception:
            return self.fallback

class ErrorHandlingSkip(Stage):
    def __init__(self, inner_stage):
        self.inner = inner_stage

    def process(self, record):
        try:
            return self.inner.process(record)
        except Exception:
            return None

class JSONSerialization(Stage):
    def process(self, record):
        if isinstance(record, str):
            return json.loads(record)
        else:
            return json.dumps(record)

class BackpressureControl(Stage):
    def __init__(self, low=0, high=1000):
        self.low = low
        self.high = high
        self.count = 0
        self.throttled = False
        self.lock = threading.Lock()

    def process(self, record):
        with self.lock:
            self.count += 1
            if self.count > self.high:
                self.throttled = True
            elif self.count < self.low:
                self.throttled = False
        return record

class DynamicReconfiguration(Stage):
    def __init__(self, inner_stage, config=None):
        self.inner = inner_stage
        self.config = config or {}

    def reconfigure(self, **kwargs):
        self.config.update(kwargs)

    def process(self, record):
        if hasattr(self.inner, 'update_config'):
            self.inner.update_config(**self.config)
        return self.inner.process(record)

class BuiltInBatch(Stage):
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.buffer = []

    def process(self, record):
        self.buffer.append(record)
        if len(self.buffer) >= self.batch_size:
            batch = self.buffer
            self.buffer = []
            return batch
        return None

class BuiltInSort(Stage):
    def __init__(self, key=lambda x: x, reverse=False):
        self.key = key
        self.reverse = reverse

    def process(self, records):
        # Only sort real batches (lists); skip others
        if not isinstance(records, list):
            return None
        # attempt to sort with provided key, fallback on failure
        try:
            return sorted(records, key=self.key, reverse=self.reverse)
        except Exception:
            return sorted(records, reverse=self.reverse)

class MemoryUsageControl(Stage):
    def __init__(self, max_items=1000):
        self.max_items = max_items
        self.spilled = False

    def process(self, record):
        # Stub: no real memory check
        return record

class Versioning:
    def __init__(self):
        self.versions = []

    def add_version(self, config):
        self.versions.append(config)

    def get_latest(self):
        return self.versions[-1] if self.versions else None

class Windowing(Stage):
    def __init__(self, window_size=5, slide=1):
        self.window_size = window_size
        self.slide = slide
        self.buffer = []

    def process(self, record):
        self.buffer.append(record)
        if len(self.buffer) >= self.window_size:
            window = self.buffer[:self.window_size]
            self.buffer = self.buffer[self.slide:]
            return window
        return None

class SamplingStage(Stage):
    def __init__(self, fraction=0.1):
        self.fraction = fraction

    def process(self, record):
        if random.random() < self.fraction:
            return record
        return None

class BuiltInGroup(Stage):
    def __init__(self, key_fn):
        self.key_fn = key_fn
        self.groups = defaultdict(list)

    def process(self, record):
        k = self.key_fn(record)
        self.groups[k].append(record)
        return {k: self.groups[k]}

class BuiltInFilter(Stage):
    def __init__(self, predicate):
        self.predicate = predicate

    def process(self, record):
        if self.predicate(record):
            return record
        return None

class BuiltInMap(Stage):
    def __init__(self, func):
        self.func = func

    def process(self, record):
        return self.func(record)

class DataValidation(Stage):
    def __init__(self, schema):
        self.schema = schema

    def process(self, record):
        schema = self.schema
        # Type check
        expected_type = schema.get('type')
        if expected_type:
            if expected_type == 'object' and not isinstance(record, dict):
                return None
            if expected_type == 'array' and not isinstance(record, list):
                return None
            if expected_type == 'string' and not isinstance(record, str):
                return None
            if expected_type == 'number' and not isinstance(record, (int, float)):
                return None
            if expected_type == 'integer' and not isinstance(record, int):
                return None
            if expected_type == 'boolean' and not isinstance(record, bool):
                return None

        # Required fields
        for key in schema.get('required', []):
            if not (isinstance(record, dict) and key in record):
                return None

        # Properties type checks
        props = schema.get('properties', {})
        if isinstance(record, dict):
            for key, subschema in props.items():
                if key in record:
                    val = record[key]
                    et = subschema.get('type')
                    if et == 'object' and not isinstance(val, dict):
                        return None
                    if et == 'array' and not isinstance(val, list):
                        return None
                    if et == 'string' and not isinstance(val, str):
                        return None
                    if et == 'number' and not isinstance(val, (int, float)):
                        return None
                    if et == 'integer' and not isinstance(val, int):
                        return None
                    if et == 'boolean' and not isinstance(val, bool):
                        return None

        return record

class SchemaEnforcement(Stage):
    def __init__(self, schema):
        self.schema = schema

    def process(self, record):
        # stub: assume conforming
        return record

class PluginSystem:
    def __init__(self):
        self.plugins = {}

    def register(self, name, obj):
        self.plugins[name] = obj

    def get(self, name):
        return self.plugins.get(name)

class CachingStage(Stage):
    def __init__(self, maxsize=128):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    def process(self, key):
        if key in self.cache:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        # stub: generate value
        value = key
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)
        return value
