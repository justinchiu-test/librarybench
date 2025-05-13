import pytest
from onboarding.branching import branch_flow

def flow_a(ctx):
    return "A"

def flow_b(ctx):
    return "B"

def test_branch_department():
    ctx = {'department': 'HR'}
    branches = {'HR': flow_a}
    assert branch_flow(ctx, branches) == "A"

def test_branch_os_default():
    ctx = {'os': 'Linux'}
    branches = {'Windows': flow_b}
    assert branch_flow(ctx, branches, default=flow_b) == "B"

def test_branch_missing():
    ctx = {}
    with pytest.raises(KeyError):
        branch_flow(ctx, {})
