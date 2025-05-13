import os
import json
import yaml
import tempfile
from schema_manager import export_schema, import_schema

def test_export_import_json(tmp_path):
    schema = {"a": 1, "b": {"c": 2}}
    p = tmp_path / "schema.json"
    export_schema(schema, str(p))
    loaded = import_schema(str(p))
    assert loaded == schema

def test_export_import_yaml(tmp_path):
    schema = {"x": [1, 2, 3], "y": "test"}
    p = tmp_path / "schema.yaml"
    export_schema(schema, str(p))
    loaded = import_schema(str(p))
    assert loaded == schema
