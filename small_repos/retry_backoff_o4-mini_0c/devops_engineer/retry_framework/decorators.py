import time
import functools
from .backoff import BackoffRegistry
from .history import RetryHistoryCollector
from .timeout import timeout_per_attempt

def retry(attempts=3, backoff='exponential', stop_condition=None,
          cancellation_policy=None, circuit_breaker=None,
          timeout=None, history_collector=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            strategy = BackoffRegistry.get(backoff)
            hist = history_collector or RetryHistoryCollector()
            last_exception = None

            for attempt in range(1, attempts + 1):
                # Before each attempt, check stop condition (but not cancellation—always do at least one try)
                if stop_condition and stop_condition.should_stop(hist):
                    break

                delay = strategy(attempt)
                try:
                    # wrap with timeout if requested
                    call_func = func
                    if timeout is not None:
                        call_func = timeout_per_attempt(timeout)(func)

                    # invoke via circuit breaker if provided
                    if circuit_breaker:
                        result = circuit_breaker.call(call_func, *args, **kwargs)
                    else:
                        result = call_func(*args, **kwargs)

                    # on success, record and return
                    hist.record(time.time(), delay, None, True)
                    return result
                except Exception as e:
                    # record the failure
                    hist.record(time.time(), delay, e, False)
                    last_exception = e

                    # if user asked to cancel, stop retrying now
                    if cancellation_policy and cancellation_policy.is_cancelled():
                        break

                    # otherwise wait before next attempt
                    time.sleep(delay)

            # if we got here with an exception from at least one try, re-raise it
            if last_exception:
                raise last_exception

        return wrapper
    return decorator
