"""
Utility functions for the unified workflow orchestration system.
"""
import uuid
import time
from typing import Any, Dict, List, Optional, Callable

def exponential_backoff(base_delay: float, attempt: int, backoff_factor: float = 2.0) -> float:
    """
    Compute exponential backoff delay.

    :param base_delay: The base delay in seconds.
    :param attempt: The retry attempt number (1-based).
    :param backoff_factor: The multiplier for each retry.
    :return: Delay in seconds.
    """
    return base_delay * (backoff_factor ** (attempt - 1))

def generate_id() -> str:
    """
    Generate a unique ID for tasks and workflows.

    :return: A string representing a unique ID.
    """
    return str(uuid.uuid4())

def current_time_ms() -> int:
    """
    Get current time in milliseconds.

    :return: Current time in milliseconds.
    """
    return int(time.time() * 1000)

def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """
    Safely execute a function, catching any exceptions.

    :param func: Function to execute.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    :return: Tuple of (result, exception). If execution was successful, exception is None.
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, e