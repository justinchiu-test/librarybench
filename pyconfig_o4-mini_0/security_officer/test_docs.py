from config_framework.docs import generate_docs

def test_generate_docs():
    schema = {"properties": {"k": {"type": "string"}, "n": {"type": "number"}}}
    md = generate_docs(schema)
    assert "## Properties" in md
    assert "- **k**: `string`" in md
    assert "- **n**: `number`" in md
