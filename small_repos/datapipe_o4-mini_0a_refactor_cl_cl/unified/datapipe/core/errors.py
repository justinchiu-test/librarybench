"""
Error handling utilities for data processing pipelines.
"""
import functools
import logging

logger = logging.getLogger(__name__)

def halt_on_error(func):
    """
    Decorator that logs errors and reraises them, halting the pipeline.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function that will log and reraise any exceptions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper


def skip_error(func):
    """
    Decorator that logs errors but continues execution by returning None.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function that will log errors but continue execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = func.__name__
            if isinstance(e, (ValueError, KeyError, RuntimeError)):
                logger.warning(f"Skipping error in {func_name}: {str(e)}")
            else:
                logger.warning(f"Skipping due to error in {func_name}: {str(e)}")
            return None
    return wrapper