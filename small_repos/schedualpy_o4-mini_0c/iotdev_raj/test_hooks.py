import pytest
from iotscheduler.hooks import HookManager

def test_hooks_run_order():
    order = []
    def pre(id, info):
        order.append("pre")
    def post(id, info):
        order.append("post")
    hm = HookManager()
    hm.register(pre_hook=pre, post_hook=post)
    # simulate hooks
    hm.run_pre("t1", {})
    hm.run_post("t1", {})
    assert order == ["pre", "post"]
