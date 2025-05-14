import pytest
from config_framework.core import (
    add_cross_field_validator,
    run_cross_field_validators,
)

def test_multiple_cross_validators():
    def v1(cfg):
        if "a" not in cfg:
            raise Exception("a missing")
    def v2(cfg):
        if cfg.get("a") != 1:
            raise Exception("a not 1")
    add_cross_field_validator("v1", v1)
    add_cross_field_validator("v2", v2)
    errs = run_cross_field_validators({})
    assert ("v1", "a missing") in errs
    cfg = {"a": 2}
    errs = run_cross_field_validators(cfg)
    assert ("v2", "a not 1") in errs
