"""
Internationalization support for the Data Pipeline CLI.
"""
import os
import json
from typing import Dict, Optional, Any

class I18n:
    """
    Simple internationalization system.
    """
    
    def __init__(self, default_locale: str = "en"):
        """
        Initialize a new I18n instance.
        
        Args:
            default_locale: Default locale to use
        """
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
    
    def load_translations(self, locale: str, translations: Dict[str, str]) -> None:
        """
        Load translations for a locale.
        
        Args:
            locale: Locale code (e.g., 'en', 'fr')
            translations: Dictionary of translations
        """
        self.translations[locale] = translations
    
    def load_translations_from_file(self, locale: str, file_path: str) -> bool:
        """
        Load translations from a JSON file.
        
        Args:
            locale: Locale code
            file_path: Path to JSON file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                
            if not isinstance(translations, dict):
                return False
                
            self.translations[locale] = translations
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    def set_locale(self, locale: str) -> bool:
        """
        Set the current locale.
        
        Args:
            locale: Locale code
            
        Returns:
            True if locale was set, False if locale not available
        """
        if locale in self.translations or locale == self.default_locale:
            self.current_locale = locale
            return True
        return False
    
    def get_locale(self) -> str:
        """
        Get the current locale.
        
        Returns:
            Current locale code
        """
        return self.current_locale
    
    def get_available_locales(self) -> list:
        """
        Get all available locales.
        
        Returns:
            List of available locale codes
        """
        return list(self.translations.keys())
    
    def translate(self, key: str, locale: Optional[str] = None) -> str:
        """
        Translate a key to the specified or current locale.
        
        Args:
            key: Translation key
            locale: Locale to use (default: current locale)
            
        Returns:
            Translated string or key if not found
        """
        use_locale = locale or self.current_locale
        
        # Try to find translation for the requested locale
        if use_locale in self.translations and key in self.translations[use_locale]:
            return self.translations[use_locale][key]
        
        # Fall back to default locale
        if use_locale != self.default_locale and self.default_locale in self.translations:
            if key in self.translations[self.default_locale]:
                return self.translations[self.default_locale][key]
        
        # Return key as fallback
        return key
    
    def translate_with_vars(self, 
                           key: str, 
                           variables: Dict[str, Any], 
                           locale: Optional[str] = None) -> str:
        """
        Translate a key with variable substitution.
        
        Args:
            key: Translation key
            variables: Variables to substitute
            locale: Locale to use (default: current locale)
            
        Returns:
            Translated string with variables substituted
        """
        # Get base translation
        translation = self.translate(key, locale)
        
        # Substitute variables
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            translation = translation.replace(placeholder, str(var_value))
            
        return translation

# Global i18n instance
_i18n = I18n()

def get_i18n() -> I18n:
    """
    Get the global I18n instance.
    
    Returns:
        Global I18n instance
    """
    return _i18n

def translate(key: str, locale: Optional[str] = None) -> str:
    """
    Translate a key using the global I18n instance.
    
    Args:
        key: Translation key
        locale: Locale to use (default: current locale)
        
    Returns:
        Translated string or key if not found
    """
    return _i18n.translate(key, locale)

def translate_with_vars(key: str, 
                       variables: Dict[str, Any], 
                       locale: Optional[str] = None) -> str:
    """
    Translate a key with variable substitution using the global I18n instance.
    
    Args:
        key: Translation key
        variables: Variables to substitute
        locale: Locale to use (default: current locale)
        
    Returns:
        Translated string with variables substituted
    """
    return _i18n.translate_with_vars(key, variables, locale)


def load_translations(locale: str) -> Dict[str, str]:
    """
    Load translations for a locale.
    
    Args:
        locale: Locale code (e.g., 'en', 'es')
        
    Returns:
        Dictionary of translations or empty dict if locale not found
    """
    # Mock translations for testing
    translations = {
        'en': {
            'greet': 'Hello',
            'farewell': 'Goodbye',
            'welcome': 'Welcome to the Data Pipeline CLI',
            'error': 'An error occurred: {message}',
            'success': 'Operation completed successfully'
        },
        'es': {
            'greet': 'Hola',
            'farewell': 'Adiós',
            'welcome': 'Bienvenido a Data Pipeline CLI',
            'error': 'Ocurrió un error: {message}',
            'success': 'Operación completada con éxito'
        }
    }
    
    # Return translations for locale or empty dict if not found
    return translations.get(locale, {})