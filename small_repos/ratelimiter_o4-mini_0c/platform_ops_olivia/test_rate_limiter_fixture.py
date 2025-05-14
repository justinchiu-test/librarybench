def test_rate_limiter_fixture(rate_limiter_fixture):
    limiter = rate_limiter_fixture
    assert limiter.allow()
    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()
