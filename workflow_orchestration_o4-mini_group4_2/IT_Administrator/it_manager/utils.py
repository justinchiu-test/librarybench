from typing import Any, Callable, Tuple, Dict

def run_with_alert(
    func: Callable,
    args: Tuple[Any, ...] = (),
    kwargs: Dict[str, Any] = None,
    alert_fn: Callable[[str, str], None] = None,
    channel: str = "scheduler"
):
    """
    Call `func(*args, **kwargs)`, and on exception send an alert via
    `alert_fn(channel, "Job failed: {e}")`.
    """
    kwargs = kwargs or {}
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if alert_fn:
            alert_fn(channel, f"Job failed: {e}")
