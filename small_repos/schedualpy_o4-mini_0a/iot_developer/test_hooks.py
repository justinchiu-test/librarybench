from scheduler.hooks import HookManager

def test_hooks_execution_order():
    hm = HookManager()
    calls = []
    def pre(a):
        calls.append(f"pre-{a}")
    def post(a):
        calls.append(f"post-{a}")
    hm.add_pre_hook(pre)
    hm.add_pre_hook(lambda a: calls.append(f"pre2-{a}"))
    hm.add_post_hook(post)
    hm.run_pre("X")
    hm.run_post("Y")
    assert calls == ["pre-X", "pre2-X", "post-Y"]
