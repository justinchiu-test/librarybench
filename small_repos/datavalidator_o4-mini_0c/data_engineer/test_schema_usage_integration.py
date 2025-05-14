import pytest
from etl_validator.schema import SchemaDefinition
from etl_validator.validator import Validator
from etl_validator.plugins import PluginManager

def test_full_integration(tmp_path):
    # Define schema and save as YAML
    schema_data = {
        'fields': {
            'id': {'type': 'string', 'required': True},
            'status': {'type': 'string', 'values': ['A', 'B'], 'required': True},
            'amount': {'type': 'number', 'min': 0, 'max': 10},
        },
        'strict': True
    }
    schema_file = tmp_path / "schema.yaml"
    schema = SchemaDefinition(schema_data)
    schema.to_yaml(str(schema_file))
    loaded = SchemaDefinition.load_yaml(str(schema_file))

    pm = PluginManager()
    val = Validator(loaded, plugin_manager=pm)

    good = {'id': 'x', 'status': 'A', 'amount': 5}
    bad = {'id': 'y', 'status': 'C', 'amount': -1}
    r1 = val.validate(good)
    r2 = val.validate(bad)

    assert r1.success
    assert not r2.success
    codes = set(e['code'] for e in r2.errors)
    assert 'ENUM' in codes and 'RANGE' in codes
