import os
from osscli.validators import validate_input
import pytest
def test_validate_type_and_range_and_regex_and_exists(tmp_path):
    assert validate_input(5, type_=int, range_=(1,10))
    assert validate_input("abc", regex=r"a.c")
    f = tmp_path / "f.txt"
    f.write_text("x")
    assert validate_input(str(f), exists=True)
    with pytest.raises(ValueError):
        validate_input("bad", type_=int)
    with pytest.raises(ValueError):
        validate_input(0, range_=(1,3))
    with pytest.raises(ValueError):
        validate_input("x", regex=r"^a")
    with pytest.raises(ValueError):
        validate_input("nope", exists=True)
