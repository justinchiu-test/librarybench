from devops_cli.hooks import HookRegistry

def test_hooks_execution():
    registry = HookRegistry()
    seq = []
    def pre(a): seq.append(f"pre{a}")
    def post(a): seq.append(f"post{a}")
    registry.register_pre(pre)
    registry.register_post(post)
    registry.execute_pre(1)
    registry.execute_post(2)
    assert seq == ["pre1", "post2"]
