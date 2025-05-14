import pytest
from src.personas.data_scientist.datapipeline_cli.config_validator import validate_config

def test_validate_config_success():
    config = {'a': 1, 'b': 'x', 'c': True}
    schema = {'a': {'type': 'integer'}, 'b': {'type': 'string'}, 'c': {'type': 'boolean'}}
    assert validate_config(config, schema) is True

def test_validate_config_missing_key():
    config = {'a': 1}
    schema = {'a': {'type': 'integer'}, 'b': {'type': 'string'}}
    with pytest.raises(ValueError):
        validate_config(config, schema)

def test_validate_config_wrong_type():
    config = {'a': '1'}
    schema = {'a': {'type': 'integer'}}
    with pytest.raises(ValueError):
        validate_config(config, schema)
