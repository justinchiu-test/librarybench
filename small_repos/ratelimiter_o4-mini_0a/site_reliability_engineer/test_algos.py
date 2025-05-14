import pytest
from rate_limiter.algos import select_window_algo, FixedWindow, SlidingWindow, RollingWindow, TokenBucket, LeakyBucket

def test_select_window_algo_valid():
    assert isinstance(select_window_algo("fixed"), FixedWindow)
    assert isinstance(select_window_algo("sliding"), SlidingWindow)
    assert isinstance(select_window_algo("rolling"), RollingWindow)
    assert isinstance(select_window_algo("token"), TokenBucket)
    assert isinstance(select_window_algo("leaky"), LeakyBucket)

def test_select_window_algo_invalid():
    with pytest.raises(ValueError):
        select_window_algo("unknown")
