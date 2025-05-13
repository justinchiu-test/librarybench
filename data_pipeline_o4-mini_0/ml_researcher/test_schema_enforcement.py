import pytest
from pipeline.schema_enforcement import SchemaEnforcement

def test_enforce_correct():
    se = SchemaEnforcement(initial_schema={"a": int, "b": str})
    rec = {"a": 1, "b": "x"}
    assert se.enforce(rec) == rec

def test_enforce_missing_or_type():
    se = SchemaEnforcement(initial_schema={"a": int})
    with pytest.raises(ValueError):
        se.enforce({"b": 2})
    with pytest.raises(ValueError):
        se.enforce({"a": "wrong", "b": "extra"})

def test_enforce_no_new_fields():
    se = SchemaEnforcement(initial_schema={"a": int}, allow_new_fields=False)
    with pytest.raises(ValueError):
        se.enforce({"a": 1, "extra": 5})

def test_update_schema():
    se = SchemaEnforcement(initial_schema={"x": int})
    se.update_schema({"y": str})
    assert "y" in se.schema
    with pytest.raises(ValueError):
        se.update_schema({"x": str})
