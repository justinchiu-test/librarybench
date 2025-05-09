def exponential_backoff(base_delay: float, backoff_factor: float, attempt: int) -> float:
    """
    Compute exponential backoff delay.
    attempt is 1-based.
    """
    return base_delay * (backoff_factor ** (attempt - 1))
