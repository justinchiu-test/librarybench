import pytest
from iotdb.interpolation import linear_interpolation, spline_interpolation

def test_linear_numeric():
    readings = [(0, 0), (10, 10)]
    assert linear_interpolation(readings, 5) == 5
    assert linear_interpolation(readings, 0) is None
    assert linear_interpolation(readings, 10) is None

def test_linear_dict():
    readings = [(0, {'a': 0}), (10, {'a': 10})]
    res = linear_interpolation(readings, 5)
    assert isinstance(res, dict) and res['a'] == 5

def test_spline():
    readings = [(0, 0), (10, 10)]
    assert spline_interpolation(readings, 5) == 5
