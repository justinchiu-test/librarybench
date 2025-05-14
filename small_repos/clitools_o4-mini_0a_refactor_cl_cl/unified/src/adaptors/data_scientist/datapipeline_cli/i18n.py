"""Adapter for data_scientist.datapipeline_cli.i18n."""

from typing import Dict, Any
from ....cli_core.i18n import TranslationManager

# Predefined translations for demo purposes
_TRANSLATIONS = {
    'en': {
        'greet': 'Hello',
        'farewell': 'Goodbye',
        'help': 'Help',
        'error': 'Error',
        'warning': 'Warning',
        'success': 'Success'
    },
    'es': {
        'greet': 'Hola',
        'farewell': 'Adiós',
        'help': 'Ayuda',
        'error': 'Error',
        'warning': 'Advertencia',
        'success': 'Éxito'
    }
}

def load_translations(locale):
    """
    Load translations for the specified locale.

    Args:
        locale (str): Locale code (e.g., 'en', 'es').

    Returns:
        dict: Dictionary of translations or empty dict if locale not found.
    """
    return _TRANSLATIONS.get(locale, {})

def translate(key: str, translations: Dict[str, str]) -> str:
    """Translate a key using the provided translations.

    Args:
        key (str): Translation key
        translations (Dict[str, str]): Dictionary of translations

    Returns:
        str: Translated text or key if not found
    """
    return translations.get(key, key)

__all__ = ['load_translations', 'translate', 'TranslationManager']
