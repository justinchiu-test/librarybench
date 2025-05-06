# Shared utility functions for all modules
import time
from typing import Any, Callable, Tuple, Dict, Optional
from IT_Administrator.it_manager.exceptions import TaskTimeoutError, MaxRetriesExceeded

def build_alert(prefix: str, **kwargs) -> str:
    """
    Construct a simple alert message with a prefix and key=value parts.
    """
    parts = " ".join(f"{k}={v}" for k, v in kwargs.items())
    return f"{prefix} {parts}".strip()

def run_with_retry(
    func: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    timeout: Optional[float],
    max_retries: int,
    name: str
) -> Tuple[Any, int]:
    """
    Run `func(*args, **kwargs)`, retrying up to max_retries times.
    If `timeout` is given, measure execution time and raise TaskTimeoutError
    if it exceeds timeout. Returns (result, attempts) on success;
    on final failure raises MaxRetriesExceeded.
    """
    last_exc = None
    attempts = 0
    for _ in range(max_retries + 1):
        attempts += 1
        try:
            if timeout is not None:
                start = time.time()
                res = func(*args, **kwargs)
                elapsed = time.time() - start
                if elapsed > timeout:
                    raise TaskTimeoutError(f"Task '{name}' timed out after {timeout}s")
            else:
                res = func(*args, **kwargs)
            return res, attempts
        except Exception as e:
            last_exc = e
    raise MaxRetriesExceeded(f"Task '{name}' exceeded max retries ({max_retries})") from last_exc

def execute_job(
    task_callable: Callable,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    alert_channel: str = "scheduler"
) -> None:
    """
    Run a scheduled job, catching exceptions and sending an alert if it fails.
    """
    try:
        task_callable(*args, **(kwargs or {}))
    except Exception as e:
        from IT_Administrator.it_manager.alert import AlertManager
        AlertManager.send_message(alert_channel, f"Job failed: {e}")
