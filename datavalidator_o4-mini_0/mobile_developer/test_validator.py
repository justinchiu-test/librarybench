import pytest
import logging
from validator import Schema, Field

def test_optional_and_missing():
    schema = Schema()
    schema.add_field(Field('a', int))
    schema.add_field(Field('b', int, optional=True))
    data = {'a': '2'}
    res = schema.parse(data)
    assert res['a'] == 2
    assert 'b' not in res

def test_coercion():
    schema = Schema()
    schema.add_field(Field('i', int))
    schema.add_field(Field('f', float))
    schema.add_field(Field('b', bool))
    schema.add_field(Field('s', str))
    data = {'i': '3', 'f': '4.5', 'b': 'true', 's': 123}
    res = schema.parse(data)
    assert isinstance(res['i'], int) and res['i'] == 3
    assert isinstance(res['f'], float) and res['f'] == 4.5
    assert isinstance(res['b'], bool) and res['b'] is True
    assert isinstance(res['s'], str) and res['s'] == '123'

def test_alias():
    schema = Schema()
    schema.add_field(Field('my_field', int))
    data = {'myField': '5'}
    res = schema.parse(data)
    assert res['my_field'] == 5

def test_aggregated_errors_and_logging(caplog):
    caplog.set_level(logging.ERROR)
    schema = Schema()
    schema.add_field(Field('x', int))
    schema.add_field(Field('y', bool))
    data = {'x': 'abc', 'y': 'maybe'}
    res = schema.parse(data)
    assert 'x' not in res and 'y' not in res
    errors = [rec for rec in caplog.records if rec.levelno == logging.ERROR]
    assert len(errors) == 2

def test_strict_mode():
    schema = Schema(strict=True)
    schema.add_field(Field('a', int))
    with pytest.raises(Exception):
        schema.parse({'a': 'bad'})

def test_test_data_generation():
    schema = Schema()
    schema.add_field(Field('i', int))
    schema.add_field(Field('opt', str, optional=True))
    mock = schema.generate_mock()
    assert 'i' in mock and isinstance(mock['i'], int)

def test_json_schema_generation():
    schema = Schema()
    schema.add_field(Field('x', int))
    schema.add_field(Field('y', bool, optional=True))
    js = schema.to_json_schema()
    assert js['type'] == 'object'
    assert js['properties']['x']['type'] == 'integer'
    assert 'y' in js['properties']
    assert 'required' in js and 'x' in js['required'] and 'y' not in js['required']

def test_plugin_system():
    def plugin(sch):
        sch.add_field(Field('new', str))
    schema = Schema()
    schema.register_plugin(plugin)
    res = schema.parse({'new': 'hi'})
    assert res['new'] == 'hi'

def test_custom_validator():
    def cv(v):
        if v < 0:
            return "must be non-negative"
    schema = Schema()
    schema.add_field(Field('n', int, custom_validator=cv))
    res = schema.parse({'n': '5'})
    assert res['n'] == 5
    cap = {}
    # negative scenario
    res2 = schema.parse({'n': '-1'})
    assert 'n' not in res2
