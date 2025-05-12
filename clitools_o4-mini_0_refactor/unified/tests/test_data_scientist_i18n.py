from data_scientist.datapipeline_cli.i18n import load_translations

def test_load_translations_en():
    tr = load_translations('en')
    assert tr.get('greet') == 'Hello'

def test_load_translations_es():
    tr = load_translations('es')
    assert tr.get('farewell') == 'Adiós'

def test_load_translations_unknown():
    tr = load_translations('fr')
    assert tr == {}
