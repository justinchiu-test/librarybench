from task_manager.backoff import exponential_backoff

def test_backoff_without_max():
    assert exponential_backoff(1, factor=2, attempt=1) == 1
    assert exponential_backoff(1, factor=2, attempt=3) == 1 * 2**2

def test_backoff_with_max():
    # 1 * 3^(3-1) = 9, capped at 5
    assert exponential_backoff(1, factor=3, attempt=3, max_delay=5) == 5
