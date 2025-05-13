import pytest
from cli_framework.branch import branch_flow

def true_func(ctx):
    return "true branch"
def false_func(ctx):
    return "false branch"

class DummyCtx:
    pass

def test_branch_callable_true():
    ctx = DummyCtx()
    res = branch_flow(ctx, lambda: True, true_func, false_func)
    assert res == "true branch"

def test_branch_direct_false():
    ctx = DummyCtx()
    res = branch_flow(ctx, 0, true_func, false_func)
    assert res == "false branch"
