import pytest
import json
from pipeline import (
    scaffold_pipeline, run_pipeline, monitor_pipeline,
    enable_streaming, set_skip_on_error, create_counter,
    set_rate_limit, start_prometheus_exporter, Counter,
    StreamingPipeline
)

def test_scaffold_pipeline_default():
    s = scaffold_pipeline()
    data = json.loads(s)
    assert data["pipeline_name"] == "pipeline"
    assert isinstance(data["transforms"], list)

def test_run_pipeline_stream():
    p = run_pipeline(stream=True)
    assert isinstance(p, StreamingPipeline)

def test_run_pipeline_non_stream():
    with pytest.raises(ValueError):
        run_pipeline(stream=False)

def test_monitor_pipeline_counts():
    p = StreamingPipeline()
    p.create_counter("hits").increment(5)
    p.create_counter("misses").increment(2)
    counts = monitor_pipeline(p)
    assert counts["hits"] == 5
    assert counts["misses"] == 2

def test_enable_streaming_flag():
    p = StreamingPipeline()
    assert not p.streaming_enabled
    enable_streaming(p)
    assert p.streaming_enabled

def test_set_skip_on_error_flag():
    p = StreamingPipeline()
    assert not p.skip_on_error
    set_skip_on_error(p)
    assert p.skip_on_error

def test_create_counter_direct():
    c = create_counter("test")
    assert isinstance(c, Counter)
    assert c.value == 0
    c.increment(3)
    assert c.value == 3

def test_set_rate_limit_and_exporter():
    p = StreamingPipeline()
    set_rate_limit(p, 100)
    assert p.rate_limit == 100
    start_prometheus_exporter(p)
    assert p.exporter_started

def test_monitor_wrong_type():
    with pytest.raises(TypeError):
        monitor_pipeline("not a pipeline")
