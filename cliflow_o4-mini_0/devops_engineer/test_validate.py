import pytest
from cli_framework.validate import validate_params

@validate_params({'x': int, 'y': str})
def f(x, y):
    return f"{x}-{y}"

def test_validate_success():
    assert f(x=1, y='a') == "1-a"

def test_validate_failure():
    with pytest.raises(ValueError):
        f(x='wrong', y='b')
