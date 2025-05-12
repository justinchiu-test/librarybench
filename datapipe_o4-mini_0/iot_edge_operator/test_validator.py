import pytest
import json
from pathlib import Path
from pipeline.validator import validate_schema

def test_validate_schema_success(tmp_path):
    schema = {"type":"object","properties":{"a":{"type":"number"}},"required":["a"]}
    data = {"a":1}
    assert validate_schema(schema, data, schema_name="test", storage_dir=str(tmp_path)) is True
    files = list(Path(tmp_path).iterdir())
    assert not files

def test_validate_schema_failure(tmp_path):
    schema = {"type":"object","properties":{"a":{"type":"number"}},"required":["a"]}
    data = {"b":2}
    result = validate_schema(schema, data, schema_name="test", storage_dir=str(tmp_path))
    assert result is False
    files = list(Path(tmp_path).iterdir())
    assert files
    # check content
    content = files[0].read_text()
    assert json.loads(content.strip()) == data
