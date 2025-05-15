"""
Parallel processing utilities.
"""
import multiprocessing
from multiprocessing import Process, Queue
import functools

def parallelize_stages(stages, data=None):
    """
    Run processing stages in parallel.
    
    This function has multiple behaviors depending on the implementation:
    - Compliance Officer: Runs a dictionary of named stages on single input
    - IoT Engineer: Runs a list of stage functions with a shared queue
    - Quant Trader: Decorator that runs function in a separate process
    - Social Media Analyst: Runs each stage function on the same data
    
    Args:
        stages: Dictionary of stage functions, list of functions, or single function
        data: Input data to process
        
    Returns:
        Dictionary of results, tuple of (processes, queue), Process instance,
        or list of results depending on the implementation
    """
    # Quant Trader mode - decorator
    if callable(stages) and data is None:
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                p = Process(target=func, args=args, kwargs=kwargs)
                p.start()
                return p
            return wrapper
        
        return decorator(stages)
    
    # IoT Engineer mode - list of functions with shared queue
    if isinstance(stages, list) and all(callable(f) for f in stages):
        q = Queue()
        processes = []
        
        for stage_func in stages:
            p = Process(target=stage_func, args=(q,))
            p.start()
            processes.append(p)
        
        return processes, q
    
    # Social Media Analyst mode - run each stage on the same data
    if isinstance(stages, list) and isinstance(data, list):
        return [stage_func(data) for stage_func in stages]
    
    # Compliance Officer mode (default) - run each named stage on the data
    if isinstance(stages, dict):
        return {name: func(data) for name, func in stages.items()}