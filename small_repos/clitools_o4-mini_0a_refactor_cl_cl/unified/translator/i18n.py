"""
Internationalization for translator CLI tools.
"""

from typing import Dict, Any, Optional


class I18n:
    """Internationalization utilities."""
    
    def __init__(self):
        """Initialize an empty translations database."""
        self._translations = {}
    
    def load(self, locale: str, translations: Dict[str, str]) -> None:
        """
        Load translations for a locale.
        
        Args:
            locale (str): Locale code.
            translations (Dict[str, str]): Dictionary mapping keys to translations.
        """
        self._translations[locale] = translations
    
    def translate(self, key: str, locale: str) -> str:
        """
        Translate a key for a locale.
        
        Args:
            key (str): Translation key.
            locale (str): Locale code.
            
        Returns:
            str: Translated string or key if not found.
        """
        # Check if locale exists
        if locale not in self._translations:
            return key
        
        # Check if key exists for locale
        translations = self._translations[locale]
        if key not in translations:
            return key
        
        return translations[key]