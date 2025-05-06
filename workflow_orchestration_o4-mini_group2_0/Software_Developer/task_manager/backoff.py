def exponential_backoff(base_delay, factor=2, attempt=1, max_delay=None):
    delay = base_delay * (factor ** (attempt - 1))
    if max_delay is not None:
        return min(delay, max_delay)
    return delay
