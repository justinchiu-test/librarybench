import pytest
import pickle
import json
import logging
from pipeline_orchestrator import (
    export_metrics,
    configure_executor,
    acquire_distributed_lock,
    dashboard_ui,
    attach_log_context,
    start_api_server,
    run_in_sandbox,
    Job,
    set_job_priority,
    lifecycle_hooks,
    register_lifecycle_hook,
    serialize_job,
    PrometheusExporter,
    StatsDExporter,
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    AsyncExecutor,
)

def test_export_metrics_default():
    exporter = export_metrics()
    assert isinstance(exporter, PrometheusExporter)
    exporter.record("jobs", 5)
    assert exporter.metrics["jobs"] == 5

def test_export_metrics_statsd():
    exporter = export_metrics("statsd")
    assert isinstance(exporter, StatsDExporter)
    exporter.record("errors", 2)
    assert exporter.metrics["errors"] == 2

def test_export_metrics_invalid():
    with pytest.raises(ValueError):
        export_metrics("unknown")

def test_configure_executor_defaults():
    exe = configure_executor()
    assert isinstance(exe, ThreadPoolExecutor)
    assert exe.type == 'thread'

def test_configure_executor_process():
    exe = configure_executor("process")
    assert isinstance(exe, ProcessPoolExecutor)
    assert exe.type == 'process'

def test_configure_executor_async():
    exe = configure_executor("async")
    assert isinstance(exe, AsyncExecutor)
    assert exe.type == 'async'

def test_configure_executor_invalid():
    with pytest.raises(ValueError):
        configure_executor("gpu")

def test_acquire_distributed_lock_contextmanager():
    with acquire_distributed_lock("redis", "lock1") as acquired:
        assert acquired is True

def test_dashboard_ui():
    assert dashboard_ui() == "dashboard started"

def test_attach_log_context():
    logger = logging.getLogger("test")
    adapter = attach_log_context(logger, "job1", "src", "daily")
    msg = adapter.process("message", {})
    assert msg[0] == "message"
    assert msg[1]["job_id"] == "job1"
    assert msg[1]["data_source"] == "src"
    assert msg[1]["schedule"] == "daily"

def test_start_api_server():
    server = start_api_server()
    assert server.running is True
    server.stop()
    assert server.running is False

def test_run_in_sandbox():
    def add(a, b):
        return a + b
    result = run_in_sandbox(add, args=(2, 3), cpu_limit=1, mem_limit=128)
    assert result == 5

def test_set_job_priority():
    job = Job("testjob")
    assert job.priority == 0
    set_job_priority(job, 10)
    assert job.priority == 10

def test_register_lifecycle_hook():
    def startup_hook():
        return "started"
    register_lifecycle_hook("startup", startup_hook)
    assert startup_hook in lifecycle_hooks["startup"]
    # test new hook type
    def custom_hook():
        pass
    register_lifecycle_hook("custom", custom_hook)
    assert custom_hook in lifecycle_hooks["custom"]

def test_serialize_job_pickle():
    job = Job("serialize_test")
    data = serialize_job(job, serializer="pickle")
    assert isinstance(data, bytes)
    job2 = pickle.loads(data)
    assert isinstance(job2, Job)
    assert job2.name == "serialize_test"

def test_serialize_job_json():
    job = Job("serialize_json")
    data = serialize_job(job, serializer="json")
    assert isinstance(data, str)
    obj = json.loads(data)
    assert obj["name"] == "serialize_json"
    assert obj["priority"] == 0

def test_serialize_job_invalid():
    job = Job("bad")
    with pytest.raises(ValueError):
        serialize_job(job, serializer="xml")
