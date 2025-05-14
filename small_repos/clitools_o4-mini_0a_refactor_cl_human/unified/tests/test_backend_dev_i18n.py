import os
import tempfile
from src.core.i18n.manager import I18nManager

def test_no_dir(tmp_path):
    # Create a manager with a non-existent directory
    manager = I18nManager("test-app", locale_dir=str(tmp_path / "nonexistent"))
    
    # There should be minimal available locales (default + C)
    locales = manager.get_available_locales()
    assert len(locales) <= 2
    assert "en_US" in locales  # Default locale

def test_load_translations(tmp_path):
    # Create a locale directory with a translation file
    locale_dir = tmp_path / "locale" / "en_US" / "LC_MESSAGES"
    locale_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a simple MO file (here we'll just create an empty file)
    mo_file = locale_dir / "test-app.mo"
    mo_file.write_text("")
    
    # Create a manager with the locale directory
    manager = I18nManager("test-app", locale_dir=str(tmp_path / "locale"))
    
    # Check locale availability
    locales = manager.get_available_locales()
    assert "en_US" in locales
    
    # Test basic translation (will return original text due to empty MO file)
    assert manager.translate("hello") == "hello"