import pytest
from datavalidation.versioned_schemas import VersionedSchemas

def test_get_existing_schema():
    vs = VersionedSchemas()
    schema = vs.get_schema(1)
    assert isinstance(schema, dict)
    assert 'required' in schema

def test_get_nonexistent_schema():
    vs = VersionedSchemas()
    assert vs.get_schema(999) is None
