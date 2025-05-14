import json
import yaml
import os
import pytest
from etl_validator.schema import SchemaDefinition

def sample_schema():
    return {
        'fields': {
            'a': {'type': 'string', 'required': True},
            'b': {'type': 'number', 'default': 5},
        },
        'strict': True
    }

def test_json_export_import(tmp_path):
    schema = SchemaDefinition(sample_schema())
    json_file = tmp_path / "schema.json"
    schema.to_json(str(json_file))
    loaded = SchemaDefinition.load_json(str(json_file))
    assert loaded.fields == schema.fields
    assert loaded.strict == schema.strict

def test_yaml_export_import(tmp_path):
    schema = SchemaDefinition(sample_schema())
    yaml_file = tmp_path / "schema.yaml"
    schema.to_yaml(str(yaml_file))
    loaded = SchemaDefinition.load_yaml(str(yaml_file))
    assert loaded.fields == schema.fields
    assert loaded.strict == schema.strict
