from security_analyst.cli_framework.hooks import register_hook, run_hooks

def test_hooks():
    calls = []
    def pre(cmd): calls.append(("pre", cmd))
    def post(cmd): calls.append(("post", cmd))

    register_hook("test", pre, when="pre")
    register_hook("test", post, when="post")
    run_hooks("cmd1", when="pre")
    run_hooks("cmd1", when="post")
    assert ("pre", "cmd1") in calls
    assert ("post", "cmd1") in calls
