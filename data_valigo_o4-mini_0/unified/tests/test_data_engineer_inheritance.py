import pytest
from data_engineer.dataschema.inheritance import Schema

def test_schema_inheritance():
    parent = Schema({'a': 1, 'b': 2})
    child = Schema({'b': 3, 'c': 4}, parent=parent)
    fields = child.resolved_fields()
    assert fields == {'a':1, 'b':3, 'c':4}
    root = Schema({'x':0})
    assert root.resolved_fields() == {'x':0}
