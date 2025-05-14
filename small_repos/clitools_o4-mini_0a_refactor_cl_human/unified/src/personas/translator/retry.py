"""
Retry mechanism for translation operations.
Provides automatic retries with exponential backoff for unreliable operations.
"""

import time
import random
import functools
import logging
from typing import Any, Callable, List, Optional, Type, Union, TypeVar, cast

# For type annotations
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class RetryError(Exception):
    """Exception raised when all retry attempts fail."""
    
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        """
        Initialize a new retry error.
        
        Args:
            message: Error message
            last_exception: Last exception that occurred
        """
        super().__init__(message)
        self.last_exception = last_exception


class Retrier:
    """
    Retry mechanism with exponential backoff.
    Handles retrying operations that might fail transiently.
    """
    
    def __init__(self, 
                max_attempts: int = 3,
                initial_delay: float = 1.0,
                max_delay: float = 60.0,
                backoff_factor: float = 2.0,
                jitter: bool = True):
        """
        Initialize a new retrier.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Factor to increase delay by after each attempt
            jitter: Whether to add randomness to delay times
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.logger = logging.getLogger('retrier')
    
    def retry(self, 
             func: F, 
             exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
             should_retry: Optional[Callable[[Exception], bool]] = None) -> F:
        """
        Decorator to retry a function on exception.
        
        Args:
            func: Function to retry
            exceptions: Exception types to catch and retry on
            should_retry: Function to determine if retry should occur
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(
                lambda: func(*args, **kwargs),
                exceptions,
                should_retry
            )
            
        return cast(F, wrapper)
    
    def execute(self, 
               operation: Callable[[], T], 
               exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
               should_retry: Optional[Callable[[Exception], bool]] = None) -> T:
        """
        Execute an operation with retries.
        
        Args:
            operation: Function to execute
            exceptions: Exception types to catch and retry on
            should_retry: Function to determine if retry should occur
            
        Returns:
            Result of the operation
            
        Raises:
            RetryError: If all retry attempts fail
        """
        if not isinstance(exceptions, list):
            exceptions = [exceptions]
        
        attempt = 1
        last_exception = None
        
        while attempt <= self.max_attempts:
            try:
                return operation()
            except tuple(exceptions) as e:
                last_exception = e
                
                # Check if we should retry
                if should_retry and not should_retry(e):
                    break
                
                # Check if we've used all attempts
                if attempt == self.max_attempts:
                    break
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                
                # Log retry attempt
                self.logger.warning(
                    f"Attempt {attempt}/{self.max_attempts} failed: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                # Wait before retrying
                time.sleep(delay)
                
                attempt += 1
        
        # If we get here, all retries failed
        error_msg = f"Operation failed after {attempt} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
            
        raise RetryError(error_msg, last_exception)
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay time with exponential backoff.
        
        Args:
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Delay time in seconds
        """
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter (up to 25%)
            jitter_amount = delay * 0.25
            delay = delay + random.uniform(-jitter_amount, jitter_amount)
            
        return max(0, delay)  # Ensure non-negative delay


# Create global retrier for convenience
_global_retrier = Retrier()

def retry(func: Optional[F] = None, 
         exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
         should_retry: Optional[Callable[[Exception], bool]] = None) -> Any:
    """
    Decorator to retry a function on exception using global retrier.
    
    Args:
        func: Function to retry
        exceptions: Exception types to catch and retry on
        should_retry: Function to determine if retry should occur
        
    Returns:
        Decorated function or decorator
    """
    # Handle both @retry and @retry(...) syntax
    if func is None:
        return lambda f: _global_retrier.retry(f, exceptions, should_retry)
    
    return _global_retrier.retry(func, exceptions, should_retry)

def execute(operation: Callable[[], T], 
           exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
           should_retry: Optional[Callable[[Exception], bool]] = None) -> T:
    """
    Execute an operation with retries using global retrier.
    
    Args:
        operation: Function to execute
        exceptions: Exception types to catch and retry on
        should_retry: Function to determine if retry should occur
        
    Returns:
        Result of the operation
    """
    return _global_retrier.execute(operation, exceptions, should_retry)

def configure(max_attempts: int = 3, 
             initial_delay: float = 1.0, 
             max_delay: float = 60.0,
             backoff_factor: float = 2.0, 
             jitter: bool = True) -> None:
    """Configure the global retrier."""
    global _global_retrier
    _global_retrier = Retrier(max_attempts, initial_delay, max_delay, backoff_factor, jitter)