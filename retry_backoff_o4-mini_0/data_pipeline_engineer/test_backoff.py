import random
from retrylib.backoff import ExponentialBackoffStrategy, FullJitterBackoffStrategy, BackoffGeneratorInterface

def test_exponential_backoff_sequence():
    strat = ExponentialBackoffStrategy(initial_delay=1, max_delay=5)
    delays = [strat.next_backoff() for _ in range(5)]
    assert delays == [1, 2, 4, 5, 5]

def test_full_jitter_bounds():
    random.seed(42)
    base = ExponentialBackoffStrategy(initial_delay=1)
    strat = FullJitterBackoffStrategy(base_strategy=base, random_instance=random)
    delays = [strat.next_backoff() for _ in range(3)]
    assert all(0 <= d <= b for d, b in zip(delays, [1, 2, 4]))
