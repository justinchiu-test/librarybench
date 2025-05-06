# Shared utility functions for SoftwareDeveloper.tasks
import concurrent.futures

def compute_backoff(base_delay, backoff_factor, attempt):
    """
    Compute exponential backoff delay for the given attempt (1-based).
    """
    if attempt < 1:
        return 0
    return base_delay * (backoff_factor ** (attempt - 1))

def is_future_timeout(exc):
    """
    Detect whether an exception is a timeout from futures or built‐in.
    """
    return isinstance(exc, concurrent.futures.TimeoutError) or isinstance(exc, TimeoutError)

def wrap_future_timeout(task_name, timeout):
    """
    Wrap a timeout exception in our FutureTimeoutError with a standardized message.
    """
    from .executor import FutureTimeoutError
    return FutureTimeoutError(f"Task '{task_name}' timeout after {timeout} seconds")

def apply_output_keys(ctx, result, output_keys):
    """
    Normalize a task result (dict or single/tuple) to a dict of outputs,
    then write them into ctx under the given keys.
    """
    if isinstance(result, dict):
        outputs = result
    else:
        # single value or sequence
        if len(output_keys) == 1:
            outputs = {output_keys[0]: result}
        else:
            outputs = dict(zip(output_keys, result))
    for k, v in outputs.items():
        ctx[k] = v
