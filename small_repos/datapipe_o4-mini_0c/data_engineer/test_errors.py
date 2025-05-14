import logging
import pytest
from pipeline.errors import skip_on_error

def test_skip_on_error(caplog):
    @skip_on_error
    def func(x):
        if x == 0:
            raise ValueError("bad")
        return x
    assert func(1) == 1
    caplog.set_level(logging.WARNING)
    assert func(0) is None
    assert "Skipping record due to error" in caplog.text
