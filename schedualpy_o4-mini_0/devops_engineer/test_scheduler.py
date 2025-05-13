import pytest
import time
import uuid
import re

from scheduler.distributed_execution import DistributedExecution
from scheduler.pre_post_hooks import PrePostHooks
from scheduler.concurrency_limits import ConcurrencyLimits
from scheduler.workflow_chaining import WorkflowChain
from scheduler.monitoring_dashboard import MonitoringDashboard
from scheduler.docker_k8s_support import DockerK8sSupport
from scheduler.cron_expression_support import CronExpressionSupport
from scheduler.jitter_and_drift_correction import JitterDriftCorrection
from scheduler.recurring_tasks import RecurringTasks
from scheduler.plugin_architecture import PluginArchitecture

def test_distributed_execution():
    de = DistributedExecution()
    assert de.elect_leader() is None
    de.add_node('nodeB')
    de.add_node('nodeA')
    leader = de.elect_leader()
    assert leader == 'nodeA'
    assert de.start() is True
    assert de.stop() is True

def test_pre_post_hooks():
    hooks = PrePostHooks()
    calls = []
    hooks.register_pre_hook(lambda x: calls.append(('pre', x)) or x+1)
    hooks.register_post_hook(lambda y: calls.append(('post', y)) or y*2)
    pre_results = hooks.run_pre_hooks(5)
    assert pre_results == [6]
    post_results = hooks.run_post_hooks(10)
    assert post_results == [20]
    assert calls == [('pre', 5), ('post', 10)]

def test_concurrency_limits():
    cl = ConcurrencyLimits("job1", per_job_limit=2, global_limit=2)
    cl.acquire()
    cl.acquire()
    with pytest.raises(RuntimeError):
        cl.acquire()
    cl.release()
    cl.acquire()  # should succeed now
    cl.release()
    cl.release()

def test_workflow_chaining_success_and_failure():
    chain = WorkflowChain()
    chain.add_task(lambda x: x+1)
    chain.add_task(lambda x: x*2, on_success=lambda y: y+3)
    # failure task
    def fail(x):
        raise ValueError("oops")
    chain.add_task(fail, on_failure=lambda e: 0)
    result = chain.run_chain(1)
    # (1+1)=2, *2=4, on_success->7, fail triggers on_failure->0
    assert result == 0

def test_monitoring_dashboard():
    dash = MonitoringDashboard()
    assert dash.start_server() is True
    time.sleep(0.2)
    status = dash.get_status()
    assert 'timestamp' in status
    assert dash.stop_server() is True

def test_docker_k8s_support():
    dks = DockerK8sSupport({'cpu':'100m'})
    assert dks.deploy_docker("myimage:latest") is True
    assert dks.deploy_k8s("mychart", {'replicas':2}) is True
    with pytest.raises(ValueError):
        dks.deploy_docker("")
    with pytest.raises(ValueError):
        dks.deploy_k8s("", {})

def test_cron_expression_support():
    valid5 = "*/5 * * * *"
    valid6 = "0 */2 * * * *"
    assert CronExpressionSupport.validate(valid5) is True
    assert CronExpressionSupport.validate(valid6) is True
    with pytest.raises(ValueError):
        CronExpressionSupport.validate("invalid cron")
    with pytest.raises(ValueError):
        CronExpressionSupport.validate("1 2 3 4")  # too few fields

def test_jitter_and_drift_correction():
    jdc = JitterDriftCorrection(max_jitter_seconds=1.0)
    base = 10.0
    for _ in range(10):
        val = jdc.apply_jitter(base)
        assert base - 1.0 <= val <= base + 1.0
    # zero jitter
    jdc0 = JitterDriftCorrection(max_jitter_seconds=0)
    assert jdc0.apply_jitter(base) == base

def test_recurring_tasks():
    rt = RecurringTasks()
    def task(): pass
    job_id = rt.schedule_recurring("job1", "*/10 * * * *", task)
    assert isinstance(uuid.UUID(job_id), uuid.UUID)
    jobs = rt.get_jobs()
    assert job_id in jobs
    assert jobs[job_id]['name'] == "job1"
    with pytest.raises(ValueError):
        rt.schedule_recurring("bad", "a b c", 123)

def test_plugin_architecture():
    pa = PluginArchitecture()
    pa.register_plugin('serializers', 'json')
    pa.register_plugin('serializers', 'protobuf')
    pa.register_plugin('transports', 'nats')
    ser = pa.get_plugins('serializers')
    tra = pa.get_plugins('transports')
    assert ser == ['json', 'protobuf']
    assert tra == ['nats']
    assert pa.get_plugins('unknown') == []
