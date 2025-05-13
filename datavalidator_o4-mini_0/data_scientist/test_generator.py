from schema_validator.schema_validator import Field, SchemaValidator

def test_sample_optional_defaults():
    schema = [
        Field("a", int),
        Field("b", float, optional=True, default=1.1)
    ]
    validator = SchemaValidator(schema)
    samples = validator.sample(20)
    # should include default occasionally and random otherwise
    has_default = any(rec["b"] == 1.1 for rec in samples)
    assert has_default

def test_json_schema_aliases_reported():
    schema = [Field("a", int, aliases=["alpha"])]
    validator = SchemaValidator(schema)
    js = validator.to_json_schema()
    prop = js["properties"]["a"]
    assert "aliases" in prop and prop["aliases"] == ["alpha"]
