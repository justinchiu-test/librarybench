import pytest
from config_manager.merge_strategies import append_strategy, replace_strategy, register_strategy, get_strategy

def test_append_strategy():
    assert append_strategy([1, 2], [3, 4]) == [1, 2, 3, 4]
    assert append_strategy(None, [5]) == [5]

def test_replace_strategy():
    assert replace_strategy([1, 2], [3]) == [3]
    assert replace_strategy(None, [7,8]) == [7,8]

def test_custom_strategy():
    def rev(existing, new):
        return list(reversed(new))
    register_strategy("rev", rev)
    strat = get_strategy("rev")
    assert strat([1], [2,3]) == [3,2]
