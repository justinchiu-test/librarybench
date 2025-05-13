import time
from contextlib import contextmanager
from .config import EnvVarOverrides
from .backoff_registry import BackoffRegistry
from .stop_conditions import MaxAttemptsStopCondition
from .hooks import OnRetryHook, AfterAttemptHook, OnGiveUpHook
from .circuit_breaker import CircuitBreakerIntegration, CircuitOpenException

class RetryContext:
    def __init__(self, backoff_strategy=None, stop_condition=None,
                 on_retry=None, after_attempt=None, on_give_up=None,
                 circuit_breaker=None):
        cfg = EnvVarOverrides()
        # Backoff strategy
        if backoff_strategy is None:
            cls = BackoffRegistry.get(cfg.backoff_strategy)
            self.backoff = cls(base=cfg.base_delay, max_delay=cfg.max_delay)
        else:
            self.backoff = backoff_strategy
        # Stop condition
        if stop_condition is None:
            self.stop_condition = MaxAttemptsStopCondition(cfg.max_attempts)
        else:
            self.stop_condition = stop_condition
        # Hooks
        self.on_retry = on_retry or OnRetryHook()
        self.after_attempt = after_attempt or AfterAttemptHook()
        self.on_give_up = on_give_up or OnGiveUpHook()
        # Circuit breaker
        if circuit_breaker is None:
            self.circuit_breaker = CircuitBreakerIntegration(
                cfg.failure_threshold, cfg.recovery_timeout)
        else:
            self.circuit_breaker = circuit_breaker

    def call(self, func, *args, **kwargs):
        attempt = 0
        last_exception = None
        while True:
            attempt += 1
            try:
                self.circuit_breaker.before_call()
                result = func(*args, **kwargs)
                self.circuit_breaker.after_call(True)
                self.after_attempt(attempt, True, None)
                return result
            except CircuitOpenException:
                raise
            except Exception as e:
                last_exception = e
                self.circuit_breaker.after_call(False)
                self.after_attempt(attempt, False, e)
                if self.stop_condition.should_stop(attempt):
                    self.on_give_up(attempt, e)
                    raise
                delay = self.backoff.next_delay(attempt)
                self.on_retry(attempt, delay)
                time.sleep(delay)

@contextmanager
def retry_context(backoff_strategy=None, stop_condition=None,
                  on_retry=None, after_attempt=None, on_give_up=None,
                  circuit_breaker=None):
    ctx = RetryContext(backoff_strategy, stop_condition,
                       on_retry, after_attempt, on_give_up,
                       circuit_breaker)
    yield ctx
