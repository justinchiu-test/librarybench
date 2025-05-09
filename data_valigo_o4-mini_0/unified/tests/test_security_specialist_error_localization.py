import pytest
from security_specialist.securedata.error_localization import ErrorLocalization

def test_translate_default():
    el = ErrorLocalization()
    assert el.translate('missing_field') == 'missing_field'

def test_register_and_translate():
    el = ErrorLocalization()
    el.register_translation('es', {'missing_field': 'campo faltar'})
    assert el.translate('missing_field', 'es') == 'campo faltar'
    # fallback to key
    assert el.translate('other', 'es') == 'other'
