import pytest
from ml_researcher.scheduler.control import ConcurrencyControl

def test_acquire_release_global_limit():
    control = ConcurrencyControl(max_global=2)
    assert control.acquire('group1')
    assert control.acquire('group2')
    assert not control.acquire('group3')
    assert control.release('group1')
    assert control.acquire('group3')

def test_per_group_limit():
    control = ConcurrencyControl(max_global=10, max_per_group={'g1': 1})
    assert control.acquire('g1')
    assert not control.acquire('g1')
    assert control.acquire('g2')
    assert control.release('g1')
    assert control.acquire('g1')
