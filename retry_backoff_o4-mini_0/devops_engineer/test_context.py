from retry_framework.context import RetryContext, retry_context

def test_retry_context_manual():
    ctx = RetryContext()
    assert hasattr(ctx, 'history')
    ctx.history.record(0, 0, None, True)
    assert len(ctx.history.attempts) == 1

def test_retry_context_cm():
    with retry_context() as ctx:
        assert hasattr(ctx, 'history')
        ctx.history.record(0, 0, None, True)
    assert len(ctx.history.attempts) == 1
