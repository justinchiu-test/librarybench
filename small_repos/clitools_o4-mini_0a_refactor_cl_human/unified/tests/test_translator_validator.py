import os
import tempfile
from src.personas.translator.validator import validate_input
from src.personas.translator.i18n import I18n

def test_validate_input_all_valid(tmp_path):
    # Prepare i18n
    i = I18n()
    i.load('en', {'key1': 'val1', 'key2': 'val2'})
    # Create dummy bundle file
    bundle = tmp_path / 'bundle.mo'
    bundle.write_text('data')
    errors = validate_input(
        i,
        locale='en',
        required_keys=['key1', 'key2'],
        placeholders={'name': 'Hello {name}'},
        pattern=r'en|fr',
        bundle_path=str(bundle)
    )
    assert errors == []

def test_validate_input_errors(tmp_path):
    i = I18n()
    i.load('en', {'key1': 'val1'})
    # No bundle file created
    errors = validate_input(
        i,
        locale='de',
        required_keys=['key1', 'key2'],
        placeholders={'name': 'No placeholder here'},
        pattern=r'en|fr',
        bundle_path=str(tmp_path / 'missing.mo')
    )
    assert any("Missing translation for key: key2" in e for e in errors)
    assert any("Invalid placeholder: name" in e for e in errors)
    assert any("Locale de does not match pattern" in e for e in errors)
    assert any("Bundle path does not exist" in e for e in errors)
