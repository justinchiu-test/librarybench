import pytest
from validator import Schema, Field, Validator

def test_empty_batch():
    schema = Schema(fields={'id': Field(int)})
    v = Validator(schema)
    summary = v.validate_batch([])
    assert summary['total'] == 0
    assert summary['passed'] == 0
    assert summary['failed'] == 0
    assert summary['errors'] == []
