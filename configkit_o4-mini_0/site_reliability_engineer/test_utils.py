import pytest
from srectl.utils import nested_merge, custom_coerce

def test_nested_merge_primitives():
    a = {'x': 1, 'y': {'z': 2}, 'l': [1,2]}
    b = {'x': 3, 'y': {'w': 4}, 'l': [5]}
    merged = nested_merge(a, b)
    assert merged['x'] == 3
    assert merged['y']['z'] == 2
    assert merged['y']['w'] == 4
    assert merged['l'] == [5]

def test_custom_coerce():
    assert custom_coerce('50%') == 0.5
    assert custom_coerce('100ms') == 0.1
    assert custom_coerce('2s') == 2.0
    assert custom_coerce('1m') == 60.0
    assert custom_coerce('100r/s') == 100.0
    assert custom_coerce('3.14') == 3.14
    assert custom_coerce('42') == 42
    assert custom_coerce(5) == 5
    assert custom_coerce('not_a_number') == 'not_a_number'
