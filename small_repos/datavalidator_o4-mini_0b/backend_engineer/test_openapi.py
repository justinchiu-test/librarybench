from validation import Schema, Field
from validation.openapi import generate_openapi_schema

def test_openapi_schema():
    fields = [
        Field("x", int, required=True, alias="X"),
        Field("y", str, required=False, default="foo"),
    ]
    schema = Schema(fields)
    doc = generate_openapi_schema(schema, title="MySchema")
    comp = doc["components"]["schemas"]["MySchema"]
    props = comp["properties"]
    assert props["X"]["type"] == "integer"
    assert "X" in comp["required"]
    assert props["y"]["default"] == "foo"
    assert props["y"]["type"] == "string"
