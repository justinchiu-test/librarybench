import pytest
from unified.src.data_engineer.dataschema.error_localization import ErrorLocalization

def test_basic_translation():
    el = ErrorLocalization()
    el.register('ERR01', 'en', 'Error occurred: {detail}')
    el.register('ERR01', 'es', 'Error ocurrió: {detail}')
    msg_en = el.translate('ERR01', 'en', detail='oops')
    msg_es = el.translate('ERR01', 'es', detail='fallo')
    assert msg_en == 'Error occurred: oops'
    assert msg_es == 'Error ocurrió: fallo'

def test_fallback_and_unknown():
    el = ErrorLocalization()
    el.register('E', 'en', 'Default {x}')
    assert el.translate('E', 'fr', x=1) == 'Default 1'
    assert el.translate('UNKNOWN', 'en') == 'UNKNOWN'
