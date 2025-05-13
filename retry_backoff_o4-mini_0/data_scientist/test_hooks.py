from retry_engine.hooks import OnRetryHook, AfterAttemptHook, OnGiveUpHook

def test_default_hooks_do_nothing():
    # Should not raise
    OnRetryHook()(1, 0.1)
    AfterAttemptHook()(1, True, None)
    OnGiveUpHook()(1, Exception())
