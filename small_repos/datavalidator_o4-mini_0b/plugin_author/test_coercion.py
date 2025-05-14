from plugin_ext.plugin import Plugin

def test_coerce_integer_and_number_and_string():
    plugin = Plugin()
    data = {'age': '30', 'price': '19.99', 'name': 'Alice'}
    schema = {
        'properties': {
            'age': {'type': 'integer'},
            'price': {'type': 'number'},
            'name': {'type': 'string'}
        }
    }
    result = plugin.coerce(data, schema)
    assert isinstance(result['age'], int) and result['age'] == 30
    assert isinstance(result['price'], float) and result['price'] == pytest.approx(19.99)
    assert isinstance(result['name'], str) and result['name'] == 'Alice'
