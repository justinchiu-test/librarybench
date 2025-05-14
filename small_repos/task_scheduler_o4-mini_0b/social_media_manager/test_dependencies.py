import pytest
from postscheduler.dependencies import define_dependency

def test_define_dependency_simple():
    deps = {
        "post2": ["post1"],
        "post3": ["post2"],
        "post1": []
    }
    order = define_dependency(deps)
    # post1 before post2 before post3
    assert order.index("post1") < order.index("post2") < order.index("post3")

def test_define_dependency_cycle():
    deps = {
        "a": ["b"],
        "b": ["a"]
    }
    with pytest.raises(ValueError):
        define_dependency(deps)
