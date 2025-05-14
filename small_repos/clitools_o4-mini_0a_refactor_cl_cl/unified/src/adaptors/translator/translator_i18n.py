"""Adapter for translator.translator_i18n."""

from typing import Dict, Any, Optional

class Translator:
    """Simple translator for internationalization."""
    
    def __init__(self, translations: Dict[str, Dict[str, str]] = None):
        """Initialize with optional translations dictionary."""
        self.translations = translations or {}
    
    def load(self, language: str, translations: Dict[str, str]) -> None:
        """Load translations for a language."""
        self.translations[language] = translations
    
    def translate(self, key: str, language: str = 'en', fallback: Optional[str] = None) -> str:
        """Translate a key to the specified language."""
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        return fallback or key
