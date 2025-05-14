import time
from .stop_conditions import MaxAttemptsStopCondition
from .circuit_breaker import CircuitOpenException

class retry_context:
    def __init__(
        self,
        backoff_strategy,
        stop_condition,
        circuit_breaker=None,
        on_retry_hook=None,
        after_attempt_hook=None,
        on_giveup_hook=None,
        env_overrides=None
    ):
        self.backoff_strategy = backoff_strategy
        self.stop_condition = stop_condition
        self.circuit_breaker = circuit_breaker
        self.on_retry_hook = on_retry_hook or (lambda attempt, delay: None)
        self.after_attempt_hook = after_attempt_hook or (lambda attempt, exception, result: None)
        self.on_giveup_hook = on_giveup_hook or (lambda attempt, exception: None)
        if env_overrides is not None:
            if isinstance(self.stop_condition, MaxAttemptsStopCondition):
                new_max = env_overrides.get_max_attempts(self.stop_condition.max)
                self.stop_condition.max = new_max
            if hasattr(self.backoff_strategy, 'base'):
                new_base = env_overrides.get_base(self.backoff_strategy.base)
                self.backoff_strategy.base = new_base
            if hasattr(self.backoff_strategy, 'cap'):
                new_cap = env_overrides.get_cap(self.backoff_strategy.cap)
                self.backoff_strategy.cap = new_cap

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def attempt(self, func, *args, **kwargs):
        attempt = 0
        while True:
            attempt += 1
            if self.circuit_breaker is not None:
                try:
                    self.circuit_breaker.before_call()
                except CircuitOpenException as e:
                    self.on_giveup_hook(attempt, e)
                    raise
            try:
                result = func(*args, **kwargs)
                if self.circuit_breaker is not None:
                    self.circuit_breaker.after_call(True)
                self.after_attempt_hook(attempt, None, result)
                return result
            except Exception as e:
                if self.circuit_breaker is not None:
                    self.circuit_breaker.after_call(False)
                self.after_attempt_hook(attempt, e, None)
                if self.stop_condition(attempt):
                    self.on_giveup_hook(attempt, e)
                    raise
                delay = self.backoff_strategy.delay(attempt)
                self.on_retry_hook(attempt, delay)
                time.sleep(delay)
