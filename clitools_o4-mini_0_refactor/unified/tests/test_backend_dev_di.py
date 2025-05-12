import pytest
from backend_dev.microcli.di import init_di

class A:
    pass

class B:
    pass

def test_init_and_resolve():
    deps = {"a": A, "b": B}
    container = init_di(deps)
    a1 = container.resolve("a")
    a2 = container.resolve("a")
    assert isinstance(a1, A)
    assert a1 is a2
    with pytest.raises(KeyError):
        container.resolve("c")
