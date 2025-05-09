"""
Utility functions for the workflow system.
"""

def exponential_backoff(base_delay: float, attempt: int) -> float:
    """
    Compute exponential backoff delay.

    :param base_delay: The base delay in seconds.
    :param attempt: The retry attempt number (1-based).
    :return: Delay in seconds.
    """
    return base_delay * (2 ** (attempt - 1))
