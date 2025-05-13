import pytest
from adapters.translator.i18n import I18n

def test_translate_existing_and_missing():
    i = I18n()
    i.load('fr', {'hello': 'bonjour'})
    assert i.translate('hello', 'fr') == 'bonjour'
    # Missing key returns key itself
    assert i.translate('bye', 'fr') == 'bye'
    # Missing locale returns key
    assert i.translate('hello', 'es') == 'hello'