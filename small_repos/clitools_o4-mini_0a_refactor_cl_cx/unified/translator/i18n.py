class I18n:
    """
    Simple internationalization (i18n) class for managing translations
    """
    
    def __init__(self):
        """Initialize with empty translations"""
        self.translations = {}
        
    def load(self, locale, translations):
        """
        Load translations for a specific locale
        
        Args:
            locale: Locale code (e.g., 'en', 'fr', 'es')
            translations: Dictionary of key -> translated text
        """
        if locale not in self.translations:
            self.translations[locale] = {}
        
        self.translations[locale].update(translations)
        
    def translate(self, key, locale):
        """
        Translate a key to the specified locale
        
        Args:
            key: The translation key
            locale: Target locale for translation
            
        Returns:
            str: Translated text or the key itself if not found
        """
        # If locale doesn't exist in our translations, return the key itself
        if locale not in self.translations:
            return key
            
        # Return translation or key if not found
        return self.translations[locale].get(key, key)