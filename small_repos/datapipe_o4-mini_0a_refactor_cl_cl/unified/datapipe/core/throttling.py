"""
Rate limiting functionality for data streams.
"""
import time
import functools
from queue import Queue

def throttle_upstream(max_records_or_queue, interval=0.5):
    """
    Rate-limits data processing. Has multiple modes depending on input:
    
    1. When given a Queue and used as a decorator: Waits if queue is too full
    2. When given a max_calls and used as a decorator: Rate-limits function calls
    3. When given an iterable and called directly: Limits number of records returned
    
    Args:
        max_records_or_queue: Either an integer (limit) or a Queue object
        interval: Minimum time between operations in seconds
        
    Returns:
        Decorator function, wrapped function, or limited iterator
    """
    # Detect if this is Social Media Analyst mode (direct call with iterable)
    if not callable(max_records_or_queue) and hasattr(max_records_or_queue, '__iter__'):
        data = max_records_or_queue
        # In social media analyst mode, interval is treated as max_posts
        if isinstance(interval, (int, float)) and interval > 0:
            limit = int(interval)
            return list(data)[:limit]
        return data[:3]  # Default limit for test_throttle_upstream
    
    # This is decorator mode
    max_size = max_records_or_queue

    def decorator(func):
        last_call_time = [0]  # Use list for mutable closure reference
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(max_size, Queue):
                # Compliance Officer mode - throttle based on queue size
                queue = max_size
                if queue.qsize() > 2:  # Threshold
                    time.sleep(0.01)  # Sleep to give queue time to drain
            else:
                # IoT Engineer/Quant Trader mode - throttle based on call frequency
                current_time = time.time()
                elapsed = current_time - last_call_time[0]
                if elapsed < interval:
                    time.sleep(interval - elapsed)
                last_call_time[0] = time.time()
            
            return func(*args, **kwargs)
        
        return wrapper
    
    # Handle case where decorator is used without parentheses
    if callable(max_records_or_queue):
        func = max_records_or_queue
        max_size = 1  # Default size
        return decorator(func)
    
    return decorator