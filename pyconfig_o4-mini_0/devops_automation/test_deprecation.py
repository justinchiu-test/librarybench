import warnings
from config_manager.deprecation import register_deprecated, check_deprecated

def test_deprecation_warning():
    register_deprecated("old", "old is deprecated")
    config = {"old": 1, "new": 2}
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        check_deprecated(config)
        assert any("deprecated" in str(wi.message) for wi in w)
