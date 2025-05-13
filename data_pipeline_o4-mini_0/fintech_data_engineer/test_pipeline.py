import pytest
import json
from pipeline import (
    Pipeline, Stage,
    ErrorHandlingRetry, ErrorHandlingFallback, ErrorHandlingSkip,
    JSONSerialization, BuiltInBatch, BuiltInSort,
    BuiltInFilter, BuiltInMap, SamplingStage,
    CachingStage, DataValidation, PluginSystem
)

def test_json_serialization_roundtrip():
    stage = JSONSerialization()
    data = {"foo": "bar", "num": 123}
    s = stage.process(data)
    assert isinstance(s, str)
    obj = stage.process(s)
    assert obj == data

def test_retry_success_after_failures():
    class FlakyStage(Stage):
        def __init__(self):
            self.count = 0
        def process(self, record):
            self.count += 1
            if self.count < 3:
                raise ValueError("fail")
            return record + 1
    flaky = FlakyStage()
    retry = ErrorHandlingRetry(flaky, retries=5)
    result = retry.process(1)
    assert result == 2

def test_retry_exhausted():
    class AlwaysFail(Stage):
        def process(self, record):
            raise RuntimeError("bad")
    retry = ErrorHandlingRetry(AlwaysFail(), retries=2)
    with pytest.raises(RuntimeError):
        retry.process(10)

def test_fallback_on_error():
    class BadStage(Stage):
        def process(self, record):
            raise KeyError
    fallback = ErrorHandlingFallback(BadStage(), fallback_value=999)
    assert fallback.process(1) == 999

def test_skip_on_error():
    class BadStage(Stage):
        def process(self, record):
            raise KeyError
    skip = ErrorHandlingSkip(BadStage())
    assert skip.process(1) is None

def test_filter_and_map_and_pipeline():
    p = Pipeline()
    p.add_stage(BuiltInFilter(lambda x: x % 2 == 0))
    p.add_stage(BuiltInMap(lambda x: x * 10))
    result = p.run(list(range(5)))
    assert result == [0, 20, 40]

def test_batch_and_sort():
    p = Pipeline()
    p.add_stage(BuiltInBatch(batch_size=3))
    p.add_stage(BuiltInSort(key=lambda lst: lst[0]))
    batches = p.run([5,3,1,4,2,0])
    # first batch [5,3,1] sorted -> [1,3,5], second [4,2,0] -> [0,2,4]
    assert batches == [[1,3,5], [0,2,4]]

def test_sampling_stage():
    stage = SamplingStage(fraction=1.0)
    records = [1,2,3]
    out = [stage.process(r) for r in records]
    assert out == records

def test_caching_stage_lru():
    cache = CachingStage(maxsize=2)
    assert cache.process("a") == "a"
    assert cache.process("b") == "b"
    # access a to make it recent
    assert cache.process("a") == "a"
    # add c, should evict b
    assert cache.process("c") == "c"
    assert "b" not in cache.cache
    assert "a" in cache.cache and "c" in cache.cache

def test_data_validation():
    schema = {"type": "object", "properties": {"x": {"type": "number"}}, "required": ["x"]}
    stage = DataValidation(schema)
    assert stage.process({"x": 5}) == {"x": 5}
    assert stage.process({"x": "no"}) is None

def test_plugin_system():
    ps = PluginSystem()
    ps.register("foo", 123)
    assert ps.get("foo") == 123
    assert ps.get("bar") is None
