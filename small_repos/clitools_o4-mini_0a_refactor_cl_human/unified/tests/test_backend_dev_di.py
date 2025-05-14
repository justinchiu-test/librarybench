import pytest
from src.core.infra.di import DependencyInjector

class A:
    pass

class B:
    pass

def test_init_and_resolve():
    # Create a dependency injector
    container = DependencyInjector()
    
    # Register classes
    container.register_class("a", A)
    container.register_class("b", B)
    
    # Resolve dependencies
    a1 = container.get("a")
    a2 = container.get("a")
    
    # Verify instances
    assert isinstance(a1, A)
    assert a1 is a2  # Same instance due to singleton behavior
    
    # Verify error handling
    with pytest.raises(KeyError):
        container.get("c")  # Non-existent dependency