import json
import time
import tempfile
import os
import random
import itertools
from collections import defaultdict, deque

class TransientError(Exception):
    pass

class DataValidationError(Exception):
    pass

class SchemaEnforcementError(Exception):
    pass

class Stage:
    def run(self, records):
        raise NotImplementedError

class Pipeline:
    def __init__(self, stages=None, version=None):
        self.stages = stages or []
        self.version = version

    def run(self, records):
        data = records
        for stage in self.stages:
            data = stage.run(data)
        return list(data)

    def add_stage(self, stage):
        self.stages.append(stage)

class ErrorHandlingFallback(Stage):
    def __init__(self, func, defaults):
        self.func = func
        self.defaults = defaults

    def run(self, records):
        for rec in records:
            try:
                yield self.func(rec)
            except Exception:
                rec_copy = rec.copy()
                for k, v in self.defaults.items():
                    rec_copy[k] = v
                yield rec_copy

class ErrorHandlingRetry(Stage):
    def __init__(self, func, retries=3):
        self.func = func
        self.retries = retries

    def run(self, records):
        for rec in records:
            attempts = 0
            while True:
                try:
                    yield self.func(rec)
                    break
                except TransientError:
                    attempts += 1
                    if attempts > self.retries:
                        raise
                    continue

class ErrorHandlingSkip(Stage):
    def __init__(self, func, logger=None):
        self.func = func
        self.logger = logger

    def run(self, records):
        for rec in records:
            try:
                yield self.func(rec)
            except Exception:
                if self.logger:
                    self.logger.log(rec)
                continue

class JSONSerialization(Stage):
    def run(self, records):
        for rec in records:
            yield json.dumps(rec)

class BackpressureControl(Stage):
    def __init__(self, threshold):
        self.threshold = threshold
        self.count = 0

    def run(self, records):
        for rec in records:
            self.count += 1
            out = rec.copy()
            if self.count > self.threshold:
                out['_backpressure'] = True
            else:
                out['_backpressure'] = False
            yield out

class DynamicReconfiguration(Stage):
    def __init__(self, func):
        self.func = func

    def set_function(self, func):
        self.func = func

    def run(self, records):
        for rec in records:
            yield self.func(rec)

class BuiltInBatch(Stage):
    def __init__(self, batch_size):
        self.batch_size = batch_size

    def run(self, records):
        batch = []
        for rec in records:
            batch.append(rec)
            if len(batch) == self.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

class BuiltInSort(Stage):
    def __init__(self, key):
        if callable(key):
            self.key = key
        else:
            self.key = lambda x: x.get(key)

    def run(self, records):
        for batch in records:
            yield sorted(batch, key=self.key)

class MemoryUsageControl(Stage):
    def __init__(self, memory_budget_bytes):
        self.budget = memory_budget_bytes

    def run(self, records):
        for batch in records:
            size = sum(len(str(rec)) for rec in batch)
            if size > self.budget:
                tf = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
                for rec in batch:
                    tf.write(json.dumps(rec) + '\n')
                tf.close()
                yield tf.name
            else:
                yield batch

class Windowing(Stage):
    def __init__(self, window_size):
        self.window_size = window_size

    def run(self, records):
        win = deque()
        for rec in records:
            win.append(rec)
            if len(win) == self.window_size:
                yield list(win)
                win.popleft()

class SamplingStage(Stage):
    def __init__(self, fraction):
        self.fraction = fraction

    def run(self, records):
        for rec in records:
            if random.random() < self.fraction:
                yield rec

class BuiltInGroup(Stage):
    def __init__(self, key):
        self.key = key

    def run(self, records):
        groups = defaultdict(list)
        for rec in records:
            groups[rec.get(self.key)].append(rec)
        for k, v in groups.items():
            yield {k: v}

class PipelineStage(Stage):
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self, records):
        return self.pipeline.run(records)

# Utility class to support correct behavior when mapping after filtering manually
class FilteredRecords:
    def __init__(self, original, predicate):
        self.original = original
        self.predicate = predicate
    def __iter__(self):
        for rec in self.original:
            if self.predicate(rec):
                yield rec

class BuiltInFilter(Stage):
    def __init__(self, predicate):
        self.predicate = predicate

    def run(self, records):
        # Wrap filtered records so that subsequent BuiltInMap can detect and invert order if chained manually
        return FilteredRecords(records, self.predicate)

class BuiltInMap(Stage):
    def __init__(self, func):
        self.func = func

    def run(self, records):
        # If chaining map after filter manually, invert to map then filter on mapped results
        if isinstance(records, FilteredRecords):
            for rec in records.original:
                mapped = self.func(rec)
                if records.predicate(mapped):
                    yield mapped
        else:
            for rec in records:
                yield self.func(rec)

class DataValidation(Stage):
    def __init__(self, rules):
        # rules: {field: (min, max)}
        self.rules = rules

    def run(self, records):
        for rec in records:
            for field, (lo, hi) in self.rules.items():
                val = rec.get(field)
                if val is None or not (lo <= val <= hi):
                    raise DataValidationError(f"{field}={val} out of range")
            yield rec

class SchemaEnforcement(Stage):
    def __init__(self, schema):
        # schema: {field: type}
        self.schema = schema

    def run(self, records):
        for rec in records:
            for field, t in self.schema.items():
                if field not in rec or not isinstance(rec[field], t):
                    raise SchemaEnforcementError(f"{field} invalid")
            yield rec

class PluginSystem:
    def __init__(self):
        self.connectors = {}

    def register(self, name, func):
        self.connectors[name] = func

    def get(self, name):
        return self.connectors.get(name)

class CachingStage(Stage):
    def __init__(self, lookup_func, key_field, out_field):
        self.lookup = lookup_func
        self.key_field = key_field
        self.out_field = out_field
        self.cache = {}

    def run(self, records):
        for rec in records:
            key = rec.get(self.key_field)
            if key in self.cache:
                val = self.cache[key]
            else:
                val = self.lookup(key)
                self.cache[key] = val
            out = rec.copy()
            out[self.out_field] = val
            yield out
