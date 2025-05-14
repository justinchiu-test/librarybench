import pytest
from src.personas.ops_engineer.cli_toolkit.di import Container

def test_container_register_and_resolve():
    c = Container()
    c.register('svc', lambda c: {'val': 123})
    inst1 = c.resolve('svc')
    inst2 = c.resolve('svc')
    assert inst1 == {'val': 123}
    assert inst1 is inst2

def test_resolve_missing():
    c = Container()
    with pytest.raises(KeyError):
        c.resolve('none')
