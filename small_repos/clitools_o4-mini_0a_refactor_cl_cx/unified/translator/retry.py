import functools
import time
import random

def retry(max_retries=3, base_delay=1, backoff=2, jitter=0.1):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        backoff: Backoff multiplier
        jitter: Random jitter to add to delay
        
    Returns:
        callable: Decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # If we've exhausted our retries, re-raise the exception
                    if retry_count >= max_retries:
                        raise
                    
                    # Calculate backoff with jitter
                    delay = base_delay * (backoff ** retry_count)
                    if jitter:
                        delay += random.uniform(0, jitter * delay)
                    
                    # Wait before retrying
                    time.sleep(delay)
                    
                    # Increment retry counter
                    retry_count += 1
                    
        return wrapper
    return decorator