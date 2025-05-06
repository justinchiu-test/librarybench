# Shared utility functions for executors, tasks, and pipelines.

def exponential_backoff(base_delay: float, backoff_factor: float, attempt: int) -> float:
    """
    Compute the backoff delay for a given retry attempt (1-based).
    """
    return base_delay * (backoff_factor ** (attempt - 1))


def map_outputs_to_context(context: dict, output_keys: list, result):
    """
    Given a result (either dict, single value, or tuple/list),
    map it back into the context dict under the provided keys.
    """
    if not output_keys:
        return
    if isinstance(result, dict):
        outputs = result
    else:
        # single value or sequence
        if len(output_keys) == 1:
            outputs = {output_keys[0]: result}
        else:
            outputs = dict(zip(output_keys, result))
    for k, v in outputs.items():
        context[k] = v


def run_callable_with_timeout(executor, fn, args: tuple, timeout: float):
    """
    Submit fn(*args) to executor and wait up to timeout seconds.
    """
    future = executor.submit(fn, *args)
    return future.result(timeout=timeout)
