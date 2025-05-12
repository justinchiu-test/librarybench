import pytest
import pipeline
from pipeline import config

def setup_function():
    # reset config before each test
    config.streaming = False
    config.skip_on_error = False

def test_scaffold_pipeline():
    result = pipeline.scaffold_pipeline("my_pipe")
    assert result == "Scaffolded pipeline at my_pipe"

def test_run_pipeline_batch_default():
    result = pipeline.run_pipeline("my_pipe")
    assert "batch" in result

def test_enable_streaming_and_run():
    pipeline.enable_streaming()
    result = pipeline.run_pipeline("my_pipe")
    assert "streaming" in result

def test_monitor_pipeline():
    result = pipeline.monitor_pipeline("p1")
    assert result == "Monitoring pipeline p1"

def test_debug_pipeline():
    result = pipeline.debug_pipeline("p2")
    assert result == "Debugging pipeline p2"

def test_set_skip_on_error():
    pipeline.set_skip_on_error()
    assert config.skip_on_error is True
