import warnings
from config_framework.deprecation import warn_deprecated, DEPRECATED_KEYS

def test_warn_deprecated():
    cfg = {"old_key": 1, "safe": 2}
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        warn_deprecated(cfg)
        assert any(DEPRECATED_KEYS["old_key"] in str(wi.message) for wi in w)
