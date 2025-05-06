def get_backoff_delay(retry_count: int, base_delay: float) -> float:
    if retry_count < 1:
        return 0.0
    return base_delay * (2 ** (retry_count - 1))
