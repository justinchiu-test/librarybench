import pytest
from configschema import validate_types, ValidationError
def test_validate_success():
    cfg = {"a": 1, "b": "txt", "c": [1,2]}
    schema = {"a": int, "b": str, "c": list}
    assert validate_types(cfg, schema)

def test_validate_failure():
    cfg = {"a": "wrong"}
    schema = {"a": int}
    with pytest.raises(ValidationError) as e:
        validate_types(cfg, schema, filename="f.ini")
    assert "expected int" in str(e.value)
