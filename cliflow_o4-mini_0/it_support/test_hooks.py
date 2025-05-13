from onboarding.hooks import register_hook, trigger_hook

def test_hooks():
    calls = []
    def hook1(ctx):
        calls.append(("h1", ctx))
    def hook2(ctx):
        calls.append(("h2", ctx))
    register_hook("pre", hook1)
    register_hook("pre", hook2)
    trigger_hook("pre", {"a":1})
    assert calls == [("h1", {"a":1}), ("h2", {"a":1})]
