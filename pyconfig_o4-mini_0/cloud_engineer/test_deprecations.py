import warnings
from config_loader.deprecations import DeprecationManager

def test_deprecation_warning_emitted():
    dm = DeprecationManager()
    dm.mark('old_key', 'Use new_key instead')
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        dm.warn_if_deprecated('old_key')
        assert len(w) == 1
        assert 'Use new_key instead' in str(w[0].message)

def test_no_warning_for_non_deprecated():
    dm = DeprecationManager()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        dm.warn_if_deprecated('other_key')
        assert len(w) == 0
