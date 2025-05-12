import pytest
from feature_pipeline.streaming import run_streaming
from feature_pipeline.serializer import registry
from feature_pipeline.metrics import PrometheusMetrics

def test_run_streaming_with_components():
    events = [{"val":"a"},{"val":5},{"val":"b"}]
    schema = {"type":"object","properties":{"val":{"type":"string"}},"required":["val"]}
    def process(event):
        return {"format":"txt","data":event["val"]+"_proc"}
    registry.register("txt", lambda data: data + "_ser")
    metrics = PrometheusMetrics()
    results = run_streaming(events, process, schema=schema, serializer=registry, metrics=metrics)
    assert results == ["a_proc_ser", "b_proc_ser"]
    assert metrics.registry.get_sample_value("records_processed") == 2.0
    assert metrics.registry.get_sample_value("records_failed") == 1.0
