"""
Internationalization support for the CLI Toolkit.
"""
import os
import json
import locale
from typing import Dict, Optional, Any, List

class I18n:
    """
    Internationalization support for the CLI Toolkit.
    """
    
    def __init__(self, default_locale: str = "en_US"):
        """
        Initialize a new I18n instance.
        
        Args:
            default_locale: Default locale to use
        """
        self.default_locale = default_locale
        self.current_locale = self._get_system_locale()
        self.translations: Dict[str, Dict[str, str]] = {}
        self._loaded_locales: List[str] = []
    
    def _get_system_locale(self) -> str:
        """
        Get the system locale.
        
        Returns:
            System locale or default locale
        """
        try:
            # Try to get the system locale
            system_locale, _ = locale.getdefaultlocale()
            if system_locale:
                return system_locale
        except (locale.Error, ValueError):
            pass
        
        # Fall back to environment variables
        for env_var in ["LC_ALL", "LC_MESSAGES", "LANG"]:
            if env_var in os.environ:
                env_locale = os.environ[env_var].split(".")[0]  # Remove encoding
                if env_locale:
                    return env_locale
        
        # Fall back to default locale
        return self.default_locale
    
    def load_translations(self, locale_code: str, translations_dict: Dict[str, str]) -> None:
        """
        Load translations for a locale.
        
        Args:
            locale_code: Locale code (e.g., "en_US")
            translations_dict: Dictionary of translations
        """
        # Normalize locale code
        locale_code = self._normalize_locale(locale_code)
        
        # Store translations
        self.translations[locale_code] = translations_dict
        
        # Add to loaded locales
        if locale_code not in self._loaded_locales:
            self._loaded_locales.append(locale_code)
    
    def load_from_file(self, locale_code: str, file_path: str) -> bool:
        """
        Load translations from a file.
        
        Args:
            locale_code: Locale code
            file_path: Path to translations file
            
        Returns:
            True if loaded successfully
        """
        # Normalize locale code
        locale_code = self._normalize_locale(locale_code)
        
        # Try to load translations
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json.load(f)
            
            # Store translations
            self.load_translations(locale_code, translations)
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    def load_from_directory(self, directory: str) -> List[str]:
        """
        Load translations from a directory.
        
        Args:
            directory: Directory containing translations files
            
        Returns:
            List of loaded locales
        """
        loaded_locales = []
        
        # Check if directory exists
        if not os.path.isdir(directory):
            return loaded_locales
        
        # Load translations files
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Skip non-JSON files
            if not filename.endswith(".json"):
                continue
            
            # Get locale code from filename
            locale_code = os.path.splitext(filename)[0]
            
            # Load translations
            if self.load_from_file(locale_code, file_path):
                loaded_locales.append(self._normalize_locale(locale_code))
        
        return loaded_locales
    
    def set_locale(self, locale_code: str) -> bool:
        """
        Set the current locale.
        
        Args:
            locale_code: Locale code
            
        Returns:
            True if locale was set
        """
        # Normalize locale code
        locale_code = self._normalize_locale(locale_code)
        
        # Check if locale is loaded
        if locale_code in self.translations or locale_code == self.default_locale:
            self.current_locale = locale_code
            return True
        
        # Check if language part matches
        lang = locale_code.split("_")[0]
        for loaded_locale in self._loaded_locales:
            if loaded_locale.startswith(lang + "_"):
                self.current_locale = loaded_locale
                return True
        
        # Locale not found
        return False
    
    def get_locale(self) -> str:
        """
        Get the current locale.
        
        Returns:
            Current locale code
        """
        return self.current_locale
    
    def get_locales(self) -> List[str]:
        """
        Get all loaded locales.
        
        Returns:
            List of loaded locale codes
        """
        return self._loaded_locales
    
    def translate(self, key: str, locale_code: Optional[str] = None) -> str:
        """
        Translate a key.
        
        Args:
            key: Translation key
            locale_code: Locale code to use (defaults to current locale)
            
        Returns:
            Translated string or key if not found
        """
        # Use specified locale or current locale
        use_locale = self._normalize_locale(locale_code) if locale_code else self.current_locale
        
        # Try to find translation in specified locale
        if use_locale in self.translations and key in self.translations[use_locale]:
            return self.translations[use_locale][key]
        
        # Try to find translation in language part of locale
        lang = use_locale.split("_")[0]
        for loaded_locale in self._loaded_locales:
            if loaded_locale.startswith(lang + "_") and key in self.translations[loaded_locale]:
                return self.translations[loaded_locale][key]
        
        # Try to find translation in default locale
        if self.default_locale in self.translations and key in self.translations[self.default_locale]:
            return self.translations[self.default_locale][key]
        
        # Return key as fallback
        return key
    
    def translate_with_vars(self, key: str, variables: Dict[str, Any], locale_code: Optional[str] = None) -> str:
        """
        Translate a key with variable substitution.
        
        Args:
            key: Translation key
            variables: Dictionary of variables to substitute
            locale_code: Locale code to use
            
        Returns:
            Translated string with variables substituted
        """
        # Get translation
        translation = self.translate(key, locale_code)
        
        # Substitute variables
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            translation = translation.replace(placeholder, str(var_value))
        
        return translation
    
    def _normalize_locale(self, locale_code: str) -> str:
        """
        Normalize a locale code.
        
        Args:
            locale_code: Locale code
            
        Returns:
            Normalized locale code
        """
        # Convert to lowercase
        locale_code = locale_code.lower()
        
        # Split language and region
        parts = locale_code.split("_")
        
        if len(parts) == 1:
            # Only language part, use default region
            return f"{parts[0]}_{parts[0].upper()}"
        
        # Language and region
        return f"{parts[0]}_{parts[1].upper()}"

# Global I18n instance
_i18n = I18n()

def get_i18n() -> I18n:
    """
    Get the global I18n instance.
    
    Returns:
        Global I18n instance
    """
    return _i18n

def translate(key: str, locale_code: Optional[str] = None) -> str:
    """
    Translate a key.
    
    Args:
        key: Translation key
        locale_code: Locale code to use
        
    Returns:
        Translated string or key if not found
    """
    return _i18n.translate(key, locale_code)

def translate_with_vars(key: str, variables: Dict[str, Any], locale_code: Optional[str] = None) -> str:
    """
    Translate a key with variable substitution.
    
    Args:
        key: Translation key
        variables: Dictionary of variables to substitute
        locale_code: Locale code to use
        
    Returns:
        Translated string with variables substituted
    """
    return _i18n.translate_with_vars(key, variables, locale_code)

def set_locale(locale_code: str) -> bool:
    """
    Set the current locale.
    
    Args:
        locale_code: Locale code
        
    Returns:
        True if locale was set
    """
    return _i18n.set_locale(locale_code)

def get_locale() -> str:
    """
    Get the current locale.
    
    Returns:
        Current locale code
    """
    return _i18n.get_locale()

def get_locales() -> List[str]:
    """
    Get all loaded locales.
    
    Returns:
        List of loaded locale codes
    """
    return _i18n.get_locales()

def load_translations(locale_code: str, translations_dict: Dict[str, str]) -> None:
    """
    Load translations for a locale.
    
    Args:
        locale_code: Locale code
        translations_dict: Dictionary of translations
    """
    _i18n.load_translations(locale_code, translations_dict)

def load_from_file(locale_code: str, file_path: str) -> bool:
    """
    Load translations from a file.
    
    Args:
        locale_code: Locale code
        file_path: Path to translations file
        
    Returns:
        True if loaded successfully
    """
    return _i18n.load_from_file(locale_code, file_path)

def load_from_directory(directory: str) -> List[str]:
    """
    Load translations from a directory.
    
    Args:
        directory: Directory containing translations files
        
    Returns:
        List of loaded locales
    """
    return _i18n.load_from_directory(directory)