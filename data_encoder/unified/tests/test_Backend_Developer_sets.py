import pytest
from nested_codec import support_homogeneous_sets

def test_homogeneous_set_ints():
    s = {1, 2, 3}
    t = support_homogeneous_sets(s)
    assert t is int

def test_homogeneous_set_strings():
    s = {"a", "b"}
    t = support_homogeneous_sets(s)
    assert t is str

def test_empty_set():
    s = set()
    t = support_homogeneous_sets(s)
    assert t is None

def test_heterogeneous_set_error():
    s = {1, "two"}
    with pytest.raises(TypeError):
        support_homogeneous_sets(s)

def test_non_set_input():
    with pytest.raises(TypeError):
        support_homogeneous_sets([1,2,3])
