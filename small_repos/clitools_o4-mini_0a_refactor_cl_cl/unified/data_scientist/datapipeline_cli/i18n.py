"""Internationalization support for data scientist CLI tools."""

from src.cli_core.i18n import TranslationManager

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