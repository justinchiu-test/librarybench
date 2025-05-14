import pytest
import data_scientist.config_manager as config_manager as cm

def test_prompt_missing_int(monkeypatch):
    inputs = iter(["", "5"])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    val = cm.prompt_missing("param", int)
    assert isinstance(val, int) and val == 5

def test_prompt_missing_list(monkeypatch):
    inputs = iter(["a,b,c"])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    val = cm.prompt_missing("param", list)
    assert isinstance(val, list) and val == ['a','b','c']

def test_validate_types_pass():
    cm.validate_types("x", 10, int)
    cm.validate_types("y", 1.2, float)
    cm.validate_types("z", [1,2], list)

def test_validate_types_fail():
    with pytest.raises(cm.ValidationError):
        cm.validate_types("x", "notint", int)

def test_numpy_array_type():
    try:
        import numpy as np
    except ImportError:
        pytest.skip("numpy not installed")
    arr = np.array([1,2,3])
    cm.validate_types("arr", arr, np.ndarray)
    with pytest.raises(cm.ValidationError):
        cm.validate_types("arr", [1,2,3], np.ndarray)
