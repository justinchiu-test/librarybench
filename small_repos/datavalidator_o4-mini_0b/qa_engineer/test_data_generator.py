from data_generator import TestDataGenerator

schema = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer', 'minimum': 0, 'maximum': 10},
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 3},
        'flag': {'type': 'boolean'}
    },
    'required': ['id', 'name'],
    'optional': ['flag']
}

def test_generate_valid():
    gen = TestDataGenerator(schema)
    payload = gen.generate_valid()
    assert isinstance(payload, dict)
    assert isinstance(payload['id'], int)
    assert isinstance(payload['name'], str)

def test_generate_invalid():
    gen = TestDataGenerator(schema)
    payload = gen.generate_invalid()
    assert isinstance(payload, dict)

def test_generate_minimal():
    gen = TestDataGenerator(schema)
    payload = gen.generate_minimal()
    assert payload['id'] == 0
    assert len(payload['name']) >= 1

def test_generate_maximal():
    gen = TestDataGenerator(schema)
    payload = gen.generate_maximal()
    assert payload['id'] == 10
    assert len(payload['name']) == 3
