"""
Retry mechanism for handling transient failures.

This module provides decorators and utilities for retrying operations.
"""

import time
import random
import functools
import logging
from typing import Callable, Type, List, Optional, Union, Any, Dict, TypeVar

# Type variables for better type hints
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, 
         base_delay: float = 1.0, 
         backoff: float = 2.0,
         jitter: float = 0.1,
         exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception) -> Callable[[F], F]:
    """
    Decorator for retrying a function if it raises specified exceptions.
    
    Args:
        max_retries (int): Maximum number of retry attempts.
        base_delay (float): Initial delay between retries in seconds.
        backoff (float): Multiplier for delay after each retry.
        jitter (float): Random factor to add to delay to prevent synchronized retries.
        exceptions (Exception or List[Exception]): Exceptions to catch and retry.
        
    Returns:
        Callable: Decorated function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # Convert single exception to list
            exception_types = exceptions
            if not isinstance(exception_types, (list, tuple)):
                exception_types = [exception_types]
            
            for attempt in range(max_retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Only catch the specified exceptions
                    if not any(isinstance(e, exc) for exc in exception_types):
                        raise
                    
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff and jitter
                        delay = base_delay * (backoff ** attempt)
                        if jitter:
                            delay += random.uniform(0, jitter * delay)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed with {type(e).__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed. "
                            f"Last error: {type(e).__name__}: {str(e)}"
                        )
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    
    return decorator


class RetryableError(Exception):
    """Base class for errors that should be retried."""
    pass


class PermanentError(Exception):
    """Base class for errors that should not be retried."""
    pass


def retry_with_handler(max_retries: int = 3, 
                      base_delay: float = 1.0, 
                      backoff: float = 2.0,
                      jitter: float = 0.1,
                      on_retry: Optional[Callable[[Exception, int], None]] = None,
                      on_give_up: Optional[Callable[[Exception], None]] = None) -> Callable[[F], F]:
    """
    Advanced retry decorator with custom handlers.
    
    Args:
        max_retries (int): Maximum number of retry attempts.
        base_delay (float): Initial delay between retries in seconds.
        backoff (float): Multiplier for delay after each retry.
        jitter (float): Random factor to add to delay to prevent synchronized retries.
        on_retry (Callable): Function to call when a retry occurs.
        on_give_up (Callable): Function to call when all retries are exhausted.
        
    Returns:
        Callable: Decorated function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except PermanentError:
                    # Don't retry permanent errors
                    raise
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff and jitter
                        delay = base_delay * (backoff ** attempt)
                        if jitter:
                            delay += random.uniform(0, jitter * delay)
                        
                        # Call on_retry handler if provided
                        if on_retry:
                            try:
                                on_retry(e, attempt)
                            except Exception as handler_error:
                                logger.warning(f"Error in retry handler: {handler_error}")
                        
                        time.sleep(delay)
                    else:
                        # Call on_give_up handler if provided
                        if on_give_up:
                            try:
                                on_give_up(e)
                            except Exception as handler_error:
                                logger.warning(f"Error in give-up handler: {handler_error}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    
    return decorator