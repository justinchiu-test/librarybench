import pytest
from src.personas.translator.di import DependencyInjector

def test_register_and_resolve():
    di = DependencyInjector()
    di.register('svc', 'service_instance')
    assert di.resolve('svc') == 'service_instance'

def test_resolve_missing_raises():
    di = DependencyInjector()
    with pytest.raises(KeyError):
        di.resolve('unknown')
