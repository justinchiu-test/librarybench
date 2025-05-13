from config_manager.docs import generate_markdown

def test_generate_markdown():
    schema = {
        "properties": {
            "foo": {"type": "string", "description": "desc foo"},
            "bar": {"type": "integer"}
        }
    }
    md = generate_markdown(schema)
    assert "# Configuration Reference" in md
    assert "## foo" in md
    assert "- Type: string" in md
    assert "- Description: desc foo" in md
    assert "## bar" in md
    assert "- Type: integer" in md
