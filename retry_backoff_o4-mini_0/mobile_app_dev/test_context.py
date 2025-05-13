import asyncio
import time
import pytest
from retry.context import retry_context
from retry.strategies import ExponentialBackoffStrategy
from retry.stop_conditions import MaxAttemptsStopCondition
from retry.circuit_breaker import CircuitBreakerIntegration, CircuitBreakerOpenException

def test_retry_context_run_success_after_retries():
    calls = []
    def flaky():
        calls.append(time.time())
        if len(calls) < 3:
            raise ValueError("fail")
        return "ok"
    on_retry_calls = []
    def on_retry(attempt, delay):
        on_retry_calls.append((attempt, delay))
    after_attempt_calls = []
    def after_attempt(attempt, success, exception, latency):
        after_attempt_calls.append((attempt, success, exception is not None, round(latency,1)))
    on_give_up_calls = []
    def on_give_up(exception):
        on_give_up_calls.append(exception)

    strategy = ExponentialBackoffStrategy(initial_delay=0.01, max_delay=0.01)
    stop = MaxAttemptsStopCondition(max_attempts=5)
    cb = CircuitBreakerIntegration(failure_threshold=10, recovery_timeout=1)
    with retry_context(strategy, stop, on_retry, after_attempt, on_give_up, cb) as ctx:
        result = ctx.run(flaky)
    assert result == "ok"
    assert len(on_retry_calls) == 2
    assert len(after_attempt_calls) == 3
    assert not on_give_up_calls

@pytest.mark.asyncio
async def test_retry_context_run_async():
    calls = []
    async def flaky():
        calls.append(time.time())
        if len(calls) < 2:
            raise RuntimeError("error")
        return "done"
    on_retry = lambda a,d: None
    after_attempt = lambda a,s,e,l: None
    on_give_up = lambda e: None
    strategy = ExponentialBackoffStrategy(initial_delay=0.01, max_delay=0.01)
    stop = MaxAttemptsStopCondition(max_attempts=3)
    with retry_context(strategy, stop, on_retry, after_attempt, on_give_up) as ctx:
        result = await ctx.run_async(flaky)
    assert result == "done"
