import pytest
from retry_lib.hooks import RetryHistoryCollector, MetricsHook, StatsDHook, PrometheusHook

class DummyClient:
    def __init__(self):
        self.count = 0
    def increment(self, name):
        self.count += 1

class DummyCounter:
    def __init__(self):
        self.value = 0
    def inc(self):
        self.value += 1

def test_retry_history_collector():
    hook = RetryHistoryCollector()
    hook.on_retry(1, Exception("e"), 0.5, {'k':'v'})
    hook.on_retry(2, Exception("e2"), 1.5, {'k':'v2'})
    assert len(hook.history) == 2
    assert hook.history[0]['attempt'] == 1
    assert abs(hook.history[1]['delay'] - 1.5) < 1e-6

def test_metrics_hook():
    hook = MetricsHook()
    hook.on_retry(1, Exception(), 0.1, {})
    hook.on_retry(2, Exception(), 0.2, {})
    assert hook.attempts == 2

def test_statsd_hook():
    client = DummyClient()
    hook = StatsDHook(client, 'metric')
    hook.on_retry(1, Exception(), 0.1, {})
    hook.on_retry(2, Exception(), 0.2, {})
    assert client.count == 2

def test_prometheus_hook():
    counter = DummyCounter()
    hook = PrometheusHook(counter)
    hook.on_retry(1, Exception(), 0.1, {})
    hook.on_retry(2, Exception(), 0.2, {})
    assert counter.value == 2
