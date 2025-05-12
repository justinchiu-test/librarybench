import pytest
from config.coercers import CustomCoercers, Color

def test_parse_vector():
    vec = CustomCoercers.parse_vector("1,2,3")
    assert vec == (1.0, 2.0, 3.0)

def test_parse_color():
    assert CustomCoercers.parse_color("Red") == Color.RED
    with pytest.raises(ValueError):
        CustomCoercers.parse_color("purple")

def test_parse_duration():
    assert CustomCoercers.parse_duration("500ms") == 0.5
    assert CustomCoercers.parse_duration("2s") == 2.0
    assert CustomCoercers.parse_duration("3m") == 180.0
    assert CustomCoercers.parse_duration("4") == 4.0
