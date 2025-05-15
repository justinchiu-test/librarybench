"""
Internationalization module for translator tools.
Provides localization string management for translations.
"""

from typing import Dict, Optional, Any


class I18n:
    """
    Simple internationalization system for translations.
    Manages translations for different locales.
    """
    
    def __init__(self):
        """Initialize a new I18n instance."""
        self.translations: Dict[str, Dict[str, str]] = {}
    
    def load(self, locale: str, translations: Dict[str, str]) -> None:
        """
        Load translations for a locale.
        
        Args:
            locale: Locale code (e.g., 'en', 'fr')
            translations: Dictionary of translations (key -> translated value)
        """
        self.translations[locale] = translations
    
    def translate(self, key: str, locale: str, default: Optional[str] = None) -> str:
        """
        Translate a key to the specified locale.
        
        Args:
            key: Translation key
            locale: Locale to translate to
            default: Default value if translation not found
            
        Returns:
            Translated string or default/key if not found
        """
        # Get translations for locale
        locale_trans = self.translations.get(locale, {})
        
        # Return translation or default/key
        return locale_trans.get(key, default if default is not None else key)
    
    def get_locales(self) -> list:
        """
        Get available locales.
        
        Returns:
            List of available locale codes
        """
        return list(self.translations.keys())