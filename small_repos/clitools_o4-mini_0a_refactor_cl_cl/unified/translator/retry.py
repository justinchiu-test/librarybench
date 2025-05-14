"""Retry utilities for translator tools."""

import time
import random
import functools

def retry(max_retries=3, base_delay=1.0, backoff=2.0, jitter=0.1):
    """Decorator for retrying a function if it raises an exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff and jitter
                        delay = base_delay * (backoff ** attempt)
                        if jitter:
                            delay += random.uniform(0, jitter * delay)
                        
                        time.sleep(delay)
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    
    return decorator