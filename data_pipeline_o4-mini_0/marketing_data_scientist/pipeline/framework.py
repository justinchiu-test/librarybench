import time
import json
import os
import pickle
from collections import defaultdict
from datetime import datetime, timedelta

# Attempt to import jsonschema; if unavailable, we'll use a minimal fallback
try:
    import jsonschema
    from jsonschema import ValidationError
    _HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None
    ValidationError = Exception
    _HAS_JSONSCHEMA = False

class Stage:
    def process(self, data):
        raise NotImplementedError

class Pipeline:
    def __init__(self, version='1.0', schema_version='1.0'):
        self.stages = []
        self.metadata = {'pipeline_version': version, 'schema_version': schema_version}

    def add_stage(self, stage):
        self.stages.append(stage)

    def remove_stage(self, stage_type):
        self.stages = [s for s in self.stages if not isinstance(s, stage_type)]

    def run(self, data):
        result = data
        for stage in self.stages:
            result = stage.process(result)
        return result

class ErrorHandlingFallback(Stage):
    def __init__(self, metrics):
        self.metrics = metrics
        self.last_values = {m: None for m in metrics}

    def process(self, data):
        out = []
        for rec in data:
            new_rec = rec.copy()
            for m in self.metrics:
                if m not in new_rec or new_rec[m] is None:
                    new_rec[m] = self.last_values.get(m)
                else:
                    self.last_values[m] = new_rec[m]
            out.append(new_rec)
        return out

class ErrorHandlingRetry(Stage):
    def __init__(self, func, retries=3, delay=0.1):
        self.func = func
        self.retries = retries
        self.delay = delay

    def process(self, data):
        attempt = 0
        while attempt < self.retries:
            try:
                return self.func(data)
            except Exception:
                attempt += 1
                time.sleep(self.delay)
        raise Exception("Max retries exceeded")

class ErrorHandlingSkip(Stage):
    def __init__(self, required_fields):
        self.required_fields = required_fields
        self.skipped = []

    def process(self, data):
        out = []
        for rec in data:
            if all(f in rec for f in self.required_fields):
                out.append(rec)
            else:
                self.skipped.append(rec)
        return out

class JSONSerialization(Stage):
    def process(self, data):
        return json.dumps(data)

class BackpressureControl(Stage):
    def __init__(self, max_buffer=100):
        self.max_buffer = max_buffer

    def process(self, data):
        if isinstance(data, list) and len(data) > self.max_buffer:
            time.sleep(0.01)
        return data

class DynamicReconfiguration:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def add_stage(self, stage):
        self.pipeline.add_stage(stage)

    def remove_stage(self, stage_type):
        self.pipeline.remove_stage(stage_type)

class BuiltInBatch(Stage):
    def __init__(self, window='hour'):
        self.window = window

    def process(self, data):
        batches = defaultdict(list)
        for rec in data:
            ts = rec.get('timestamp')
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            if self.window == 'hour':
                key = ts.replace(minute=0, second=0, microsecond=0)
            elif self.window == 'day':
                key = ts.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                key = ts
            batches[key].append(rec)
        return [{'window_start': k, 'records': v} for k, v in sorted(batches.items())]

class BuiltInSort(Stage):
    def __init__(self, key='timestamp'):
        self.key = key

    def process(self, data):
        return sorted(data, key=lambda x: x.get(self.key))

class MemoryUsageControl(Stage):
    def __init__(self, max_records=1000, spill_file='spill.pkl'):
        self.max_records = max_records
        self.spill_file = spill_file

    def process(self, data):
        if isinstance(data, list) and len(data) > self.max_records:
            with open(self.spill_file, 'wb') as f:
                pickle.dump(data, f)
            return {'spill_file': self.spill_file}
        return data

class Versioning(Stage):
    def __init__(self, pipeline_version, schema_version):
        self.pipeline_version = pipeline_version
        self.schema_version = schema_version

    def process(self, data):
        return {'data': data, 'pipeline_version': self.pipeline_version, 'schema_version': self.schema_version}

class Windowing(Stage):
    def __init__(self, mode='tumbling', size=1, unit='day'):
        self.mode = mode
        self.size = size
        self.unit = unit

    def process(self, data):
        sorted_data = sorted(data, key=lambda x: x.get('timestamp'))
        times = []
        for x in sorted_data:
            ts = x.get('timestamp')
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            times.append(ts)
        out = []
        if self.mode == 'tumbling':
            current_window = None
            bucket = []
            for rec, ts in zip(sorted_data, times):
                win = ts.date() if self.unit == 'day' else ts
                if current_window is None:
                    current_window = win
                if win != current_window:
                    out.append({'window': current_window, 'records': bucket})
                    bucket = []
                    current_window = win
                bucket.append(rec)
            if bucket:
                out.append({'window': current_window, 'records': bucket})
        else:  # sliding
            delta = timedelta(**{self.unit + 's': self.size})
            for i in range(len(times)):
                start = times[i]
                end = start + delta
                bucket = [rec for rec, ts in zip(sorted_data, times) if start <= ts < end]
                out.append({'window_start': start, 'window_end': end, 'records': bucket})
        return out

class SamplingStage(Stage):
    def __init__(self, fraction=0.1):
        self.fraction = fraction

    def process(self, data):
        cutoff = int(len(data) * self.fraction)
        return data[:cutoff]

class BuiltInGroup(Stage):
    def __init__(self, key):
        self.key = key

    def process(self, data):
        groups = defaultdict(list)
        for rec in data:
            groups[rec.get(self.key)].append(rec)
        return dict(groups)

class PipelineComposition:
    @staticmethod
    def compose(stages):
        p = Pipeline()
        for s in stages:
            p.add_stage(s)
        return p

class BuiltInFilter(Stage):
    def __init__(self, predicate):
        self.predicate = predicate

    def process(self, data):
        return [rec for rec in data if self.predicate(rec)]

class BuiltInMap(Stage):
    def __init__(self, map_func):
        self.map_func = map_func

    def process(self, data):
        return [self.map_func(rec) for rec in data]

class DataValidation(Stage):
    """
    Validate each record against the provided JSON Schema.
    Uses jsonschema library if available, otherwise applies a minimal check
    for object type, required fields, and primitive type matching.
    """
    # mapping json-schema types to Python types
    _TYPE_MAP = {
        'integer': int,
        'number': (int, float),
        'string': str,
        'boolean': bool,
        'object': dict,
        'array': list
    }

    def __init__(self, schema):
        self.schema = schema

    def process(self, data):
        for rec in data:
            if _HAS_JSONSCHEMA:
                # use jsonschema if installed
                jsonschema.validate(rec, self.schema)
            else:
                # minimal manual validation
                # check top-level type
                top_type = self.schema.get('type')
                if top_type:
                    py_type = self._TYPE_MAP.get(top_type)
                    if py_type and not isinstance(rec, py_type):
                        raise Exception(f"Record is not of type {top_type}")
                # properties
                props = self.schema.get('properties', {})
                for field, field_schema in props.items():
                    if field in rec:
                        expected_type = field_schema.get('type')
                        if expected_type:
                            py_t = self._TYPE_MAP.get(expected_type)
                            if py_t and not isinstance(rec[field], py_t):
                                raise Exception(f"Field '{field}' is not of type {expected_type}")
                # required
                for req in self.schema.get('required', []):
                    if req not in rec:
                        raise Exception(f"Missing required field '{req}'")
        return data

class SchemaEnforcement(Stage):
    def __init__(self, schema):
        self.schema = schema

    def process(self, data):
        out = []
        for rec in data:
            new_rec = {}
            for f, t in self.schema.items():
                val = rec.get(f)
                if val is not None:
                    new_rec[f] = t(val)
                else:
                    new_rec[f] = None
            out.append(new_rec)
        return out

class CachingStage(Stage):
    def __init__(self, loader_func):
        self.loader_func = loader_func
        self.cache = None

    def process(self, data):
        if self.cache is None:
            self.cache = self.loader_func()
        out = []
        for rec in data:
            enriched = rec.copy()
            key = rec.get('key')
            enriched['lookup'] = self.cache.get(key)
            out.append(enriched)
        return out
