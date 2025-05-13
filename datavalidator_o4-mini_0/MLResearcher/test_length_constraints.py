from length_constraints import validate_length

def test_validate_length():
    assert validate_length([1,2,3], 3)
    assert not validate_length([1,2], 3)
    assert not validate_length(123, 1)
