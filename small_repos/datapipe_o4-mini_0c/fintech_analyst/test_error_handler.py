import logging
import pytest
from error_handler import skip_on_error

def test_skip_on_error_decorator(caplog):
    @skip_on_error
    def faulty(x):
        if x < 0:
            raise ValueError("negative")
        return x * 2

    caplog.set_level(logging.ERROR)
    assert faulty(2) == 4
    assert faulty(-1) is None
    assert "Error processing record: negative" in caplog.text
