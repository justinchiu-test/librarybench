from config_loader.docs import generate_markdown

def test_generate_markdown():
    schema = {
        'properties': {
            'host': {'type': 'string', 'description': 'Host name'},
            'port': {'type': 'number'}
        }
    }
    md = generate_markdown(schema)
    assert '## host' in md
    assert '- Type: `string`' in md
    assert '- Description: Host name' in md
    assert '## port' in md
