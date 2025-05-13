from retrylib.hooks import OnRetryHook, AfterAttemptHook, OnGiveUpHook

def test_default_hooks_do_nothing():
    retry = OnRetryHook()
    after = AfterAttemptHook()
    giveup = OnGiveUpHook()
    # should not raise
    retry(1, 0.5)
    after(1, None, 'res')
    giveup(1, Exception("err"))
