import pytest
from pipeline.hooks import SourceSinkHooks

def test_hooks_run_in_order():
    hooks = SourceSinkHooks()
    hooks.register_pre(lambda r: r+1)
    hooks.register_pre(lambda r: r*2)
    hooks.register_post(lambda r: r-3)
    val = hooks.run_pre(3)
    assert val == 8  # (3+1)*2
    val2 = hooks.run_post(val)
    assert val2 == 5  # 8-3
