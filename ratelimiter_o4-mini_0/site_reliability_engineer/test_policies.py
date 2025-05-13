import time
import pytest
from rate_limiter.policies import TokenBucketPolicy, FixedWindowPolicy, chain_policies

def test_token_bucket_allows_and_throttles():
    tb = TokenBucketPolicy(rate=1, capacity=1)
    assert tb.allow() is True
    assert tb.allow() is False
    time.sleep(1.1)
    assert tb.allow() is True

def test_fixed_window_allows_and_throttles():
    fw = FixedWindowPolicy(limit=2, window_seconds=1)
    assert fw.allow() is True
    assert fw.allow() is True
    assert fw.allow() is False
    time.sleep(1.1)
    assert fw.allow() is True

def test_chain_policies_series():
    tb = TokenBucketPolicy(rate=1, capacity=1)
    fw = FixedWindowPolicy(limit=1, window_seconds=1)
    checker = chain_policies([tb, fw], mode="series")
    assert checker() is True
    assert checker() is False

def test_chain_policies_parallel():
    tb1 = TokenBucketPolicy(rate=0, capacity=1)
    tb2 = TokenBucketPolicy(rate=1, capacity=1)
    checker = chain_policies([tb1, tb2], mode="parallel")
    assert checker() is True
    assert checker() is True  # tb2 allows twice over time
    time.sleep(1)
    assert checker() is True
