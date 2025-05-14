import pytest
import yaml
import asyncio
from form_validator import FormValidator

def test_export_import_roundtrip():
    fv = FormValidator()
    original = fv.schema.copy()
    yaml_str = fv.export_schema()
    fv.import_schema(yaml_str)
    # After import, schema keys should match original keys
    assert set(fv.schema.keys()) == set(original.keys())
    # Check one field's properties
    assert fv.schema['age']['min'] == original['age']['min']
    assert fv.schema['age']['max'] == original['age']['max']
