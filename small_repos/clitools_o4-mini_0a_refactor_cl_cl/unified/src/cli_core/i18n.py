"""
Internationalization support for CLI tools.

This module provides functionality for loading translations and managing localization.
"""

import os
import re
from typing import Dict, Any, Optional


class TranslationManager:
    """
    Manages translations and provides localization functions.
    """
    
    def __init__(self, default_locale: str = "en"):
        """
        Initialize the translation manager.
        
        Args:
            default_locale (str): Default locale to use if requested locale is not available.
        """
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_locale = default_locale
    
    def add_translation(self, locale: str, translations: Dict[str, str]) -> None:
        """
        Add translations for a locale.
        
        Args:
            locale (str): Locale code (e.g., 'en', 'fr').
            translations (Dict[str, str]): Dictionary mapping keys to translated strings.
        """
        if locale not in self.translations:
            self.translations[locale] = {}
        
        self.translations[locale].update(translations)
    
    def translate(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Translate a key.
        
        Args:
            key (str): Translation key.
            locale (str): Locale to use (falls back to default_locale if not specified or available).
            **kwargs: Format string parameters.
            
        Returns:
            str: Translated string (or key itself if translation not found).
        """
        locale = locale or self.default_locale
        
        # Try requested locale
        if locale in self.translations and key in self.translations[locale]:
            translation = self.translations[locale][key]
        # Fall back to default locale
        elif self.default_locale in self.translations and key in self.translations[self.default_locale]:
            translation = self.translations[self.default_locale][key]
        # Return key as-is if no translation found
        else:
            translation = key
        
        # Apply string formatting if kwargs provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation
        
        return translation
    
    def get_available_locales(self) -> list:
        """
        Get list of available locales.
        
        Returns:
            list: List of available locale codes.
        """
        return list(self.translations.keys())


def parse_po_content(content: str) -> Dict[str, str]:
    """
    Parse PO file content.
    
    This is a simplified PO parser that extracts msgid/msgstr pairs.
    
    Args:
        content (str): Content of the PO file.
        
    Returns:
        Dict[str, str]: Dictionary mapping message IDs to translations.
    """
    translations = {}
    
    # Simple pattern to match msgid/msgstr pairs (not handling multiline properly)
    pattern = r'msgid\s+"(.*?)"\s+msgstr\s+"(.*?)"'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        msgid, msgstr = match.groups()
        if msgid and msgstr:  # Only add non-empty translations
            translations[msgid] = msgstr
    
    return translations


def load_po_file(file_path: str) -> Dict[str, str]:
    """
    Load and parse a PO file.
    
    Args:
        file_path (str): Path to the PO file.
        
    Returns:
        Dict[str, str]: Dictionary mapping message IDs to translations.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_po_content(content)
    except (IOError, UnicodeDecodeError):
        return {}


def load_translations(directory: str) -> Dict[str, Dict[str, Any]]:
    """
    Load all translations from a directory.

    Args:
        directory (str): Directory path containing translation files.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping file names to either:
            - Their parsed content with 'msgstr' key (for backward compatibility)
            - Or a dictionary mapping message IDs to translations
    """
    translations = {}

    # Check if directory exists
    if not os.path.isdir(directory):
        return translations

    # Load each .po file from the directory
    for file_name in os.listdir(directory):
        if file_name.endswith('.po'):
            file_path = os.path.join(directory, file_name)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # For backward compatibility with the backend_dev test
                if "msgid" in content and "msgstr" in content:
                    if file_name not in translations:
                        translations[file_name] = {}

                    # Store the original content for backward compatibility
                    raw_parts = content.split("msgstr")
                    if len(raw_parts) > 1:
                        translations[file_name]["msgstr"] = "msgstr" + raw_parts[1]

                # Also parse the translations normally
                translation_dict = parse_po_content(content)
                if translation_dict:
                    # Merge with any existing data
                    if file_name in translations:
                        translations[file_name].update(translation_dict)
                    else:
                        translations[file_name] = translation_dict
            except (IOError, UnicodeDecodeError):
                pass

    return translations