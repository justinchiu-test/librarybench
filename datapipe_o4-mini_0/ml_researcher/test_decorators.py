import logging
import pytest
from feature_pipeline.decorators import skip_on_error

def test_skip_on_error_logs_and_returns_none(caplog):
    @skip_on_error
    def faulty(x):
        raise ValueError("bad")

    caplog.set_level(logging.WARNING)
    result = faulty(1)
    assert result is None
    assert "Error in faulty: bad" in caplog.text
