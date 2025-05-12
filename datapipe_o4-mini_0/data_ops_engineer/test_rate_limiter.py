import pipeline
from pipeline import config
from pipeline.rate_limiter import set_rate_limit

def test_set_rate_limit_decorator():
    @set_rate_limit(10)
    def foo(x):
        return x * 2
    assert hasattr(foo, '_rate_limit')
    assert foo._rate_limit == 10
    assert config.rate_limit == 10
    # test function works
    assert foo(3) == 6
