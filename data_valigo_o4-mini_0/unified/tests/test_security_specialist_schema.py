import pytest
from security_specialist.securedata.schema import Schema, SchemaRegistry

def test_schema_inheritance_and_versioning():
    base = Schema('User', {'a':1, 'b':2}, version=1)
    assert base.fields == {'a':1, 'b':2}
    child = Schema('User', {'b':3, 'c':4}, version=2, parent=base)
    assert child.fields == {'a':1, 'b':3, 'c':4}
    # registry
    reg = SchemaRegistry()
    reg.register(base)
    reg.register(child)
    assert reg.get('User', 1) is base
    assert reg.get('User', 2) is child
