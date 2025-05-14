"""
Translator retry adapter.

Provides backward compatibility for translator.retry.
"""

from functools import wraps
from typing import Callable, TypeVar, Any

from ...utils.retry import retry as core_retry

# Type variables for better type hints
F = TypeVar('F', bound=Callable[..., Any])


def retry(max_retries: int = 3, base_delay: float = 1.0, 
         backoff: float = 2.0, jitter: float = 0.1) -> Callable[[F], F]:
    """
    Decorator for retrying a function if it raises an exception.
    
    Args:
        max_retries (int): Maximum number of retry attempts.
        base_delay (float): Initial delay between retries in seconds.
        backoff (float): Multiplier for delay after each retry.
        jitter (float): Random factor to add to delay to prevent synchronized retries.
        
    Returns:
        Callable: Decorated function.
    """
    return core_retry(max_retries=max_retries, base_delay=base_delay, 
                     backoff=backoff, jitter=jitter)