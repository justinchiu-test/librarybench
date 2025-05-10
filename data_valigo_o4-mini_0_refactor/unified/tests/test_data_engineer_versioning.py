import pytest
from unified.src.data_engineer.dataschema.versioning import SchemaVersioning

def test_register_and_validate():
    sv = SchemaVersioning()
    sv.register('v1', {'a': int, 'b': str})
    assert sv.validate('v1', {'a':1, 'b':'b'})
    assert not sv.validate('v1', {'a':1})

def test_migration():
    sv = SchemaVersioning()
    sv.register('v1', {'a':int})
    sv.register('v2', {'a':int, 'b':int})
    def mig(d):
        d['b'] = 0
        return d
    sv.add_migration('v1', 'v2', mig)
    data = {'a':5}
    new = sv.migrate(data, 'v1', 'v2')
    assert new == {'a':5, 'b':0}
    with pytest.raises(ValueError):
        sv.migrate(data, 'v2', 'v3')
