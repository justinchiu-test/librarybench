# Shared utility functions for timeout checks and backoff delays

def compute_delay(base_delay: float, backoff_factor: float, attempt: int) -> float:
    """
    Compute exponential backoff delay given a 1‐based attempt number.
    """
    return base_delay * (backoff_factor ** (attempt - 1))

def is_future_timeout(exc: Exception) -> bool:
    """
    Return True if exc is a timeout from concurrent futures or built‐in.
    """
    import concurrent.futures
    return isinstance(exc, concurrent.futures.TimeoutError) or isinstance(exc, TimeoutError)
