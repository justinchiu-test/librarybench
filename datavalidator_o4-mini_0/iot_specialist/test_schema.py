import pytest
import os
from telemetry.schema import export_schema, load_schema

def test_json_schema(tmp_path):
    schema = {'a': 1}
    file = tmp_path / 'test.json'
    export_schema(schema, str(file), 'json')
    loaded = load_schema(str(file))
    assert loaded == schema

def test_yaml_schema(tmp_path):
    schema = {'a': 2}
    file = tmp_path / 'test.yaml'
    export_schema(schema, str(file), 'yaml')
    loaded = load_schema(str(file))
    assert loaded == schema

def test_invalid_format(tmp_path):
    with pytest.raises(ValueError):
        export_schema({}, str(tmp_path / 'f.txt'), 'txt')
    with pytest.raises(ValueError):
        load_schema(str(tmp_path / 'f.txt'))
