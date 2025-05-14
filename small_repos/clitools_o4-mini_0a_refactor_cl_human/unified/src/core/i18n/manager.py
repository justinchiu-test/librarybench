"""
Internationalization (i18n) module for CLI tools.
Manages translations for multilingual support.
"""

import gettext
import locale
import os
from pathlib import Path
from typing import Dict, List, Optional, Set


class I18nManager:
    """
    Manages translations for internationalization.
    Provides a simple interface for locale handling and text translation.
    """
    
    def __init__(self, 
                app_name: str,
                default_locale: str = "en_US",
                locale_dir: Optional[str] = None,
                fallback: bool = True):
        """
        Initialize a new internationalization manager.
        
        Args:
            app_name: Name of the application
            default_locale: Default locale to use when preferred locale is not available
            locale_dir: Directory containing translations (None for auto-detection)
            fallback: Whether to fall back to default locale if requested locale not found
        """
        self.app_name = app_name
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.fallback = fallback
        self.translators: Dict[str, gettext.NullTranslations] = {}
        self.available_locales: Set[str] = set()
        
        # Determine locale directory
        if locale_dir:
            self.locale_dir = locale_dir
        else:
            # Try to find locale directory in common locations
            possible_dirs = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'locales'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'locale'),
                os.path.join('/usr', 'share', 'locale'),
                os.path.join('/usr', 'local', 'share', 'locale'),
            ]
            for d in possible_dirs:
                if os.path.exists(d):
                    self.locale_dir = d
                    break
            else:
                # Default to current directory
                self.locale_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          '..', '..', 'locales')
                os.makedirs(self.locale_dir, exist_ok=True)
        
        # Load available locales
        self._load_available_locales()
        
        # Initialize with system locale
        self.set_locale(self._get_system_locale())
    
    def set_locale(self, locale_name: str) -> bool:
        """
        Set the current locale.
        
        Args:
            locale_name: Locale to set (e.g., "en_US", "fr_FR")
            
        Returns:
            True if locale was set successfully, False otherwise
        """
        # Check if locale is available
        if locale_name not in self.available_locales:
            if not self.fallback:
                return False
            locale_name = self.default_locale
        
        # Load translator if needed
        if locale_name not in self.translators:
            self._load_translator(locale_name)
        
        self.current_locale = locale_name
        return True
    
    def translate(self, text: str, **kwargs) -> str:
        """
        Translate text to the current locale.
        Supports variable interpolation with named placeholders.
        
        Args:
            text: Text to translate
            **kwargs: Variables for interpolation
            
        Returns:
            Translated text with variables interpolated
        """
        # Get translator for current locale
        translator = self.translators.get(self.current_locale)
        if not translator:
            return text
        
        # Translate
        translated = translator.gettext(text)
        
        # Apply variable substitutions if any
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except KeyError:
                # If format fails, just return the raw translated text
                pass
        
        return translated
    
    def get_available_locales(self) -> List[str]:
        """
        Get list of available locales.
        
        Returns:
            List of available locale codes
        """
        return sorted(list(self.available_locales))
    
    def _get_system_locale(self) -> str:
        """
        Get the system locale.
        
        Returns:
            System locale code (e.g., "en_US")
        """
        try:
            # Try to get from environment
            for env_var in ['LC_ALL', 'LC_MESSAGES', 'LANG']:
                if env_var in os.environ:
                    env_locale = os.environ[env_var].split('.')[0]
                    if env_locale:
                        return env_locale
            
            # Try locale module
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale:
                return sys_locale
        except Exception:
            pass
        
        # Default to default_locale
        return self.default_locale
    
    def _load_available_locales(self) -> None:
        """Load available locales from the locale directory."""
        # Always add default locale
        self.available_locales.add(self.default_locale)
        
        # Add special "C" locale which is just ASCII
        self.available_locales.add("C")
        
        try:
            locale_dir = Path(self.locale_dir)
            if locale_dir.exists():
                for path in locale_dir.iterdir():
                    if path.is_dir() and (path / f"{self.app_name}.mo").exists():
                        self.available_locales.add(path.name)
        except Exception:
            # If any error occurs, just use the defaults
            pass
    
    def _load_translator(self, locale_name: str) -> None:
        """
        Load translator for a specific locale.
        
        Args:
            locale_name: Locale to load
        """
        try:
            trans = gettext.translation(
                self.app_name,
                localedir=self.locale_dir,
                languages=[locale_name],
                fallback=True
            )
            self.translators[locale_name] = trans
        except Exception:
            # If loading fails, use NullTranslations (no translation)
            self.translators[locale_name] = gettext.NullTranslations()


class POFile:
    """Helper class for working with PO files."""
    
    @staticmethod
    def extract_messages(source_file: str, output_file: str) -> bool:
        """
        Extract translatable messages from a source file.
        Requires the 'xgettext' command-line tool.
        
        Args:
            source_file: Source file to extract messages from
            output_file: Output PO file
            
        Returns:
            True if extraction succeeded, False otherwise
        """
        try:
            import subprocess
            result = subprocess.run([
                'xgettext',
                '--language=Python',
                f'--output={output_file}',
                source_file
            ], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def compile_po(po_file: str, mo_file: str) -> bool:
        """
        Compile a PO file to a MO file.
        Requires the 'msgfmt' command-line tool.
        
        Args:
            po_file: Input PO file
            mo_file: Output MO file
            
        Returns:
            True if compilation succeeded, False otherwise
        """
        try:
            import subprocess
            result = subprocess.run([
                'msgfmt',
                f'--output-file={mo_file}',
                po_file
            ], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False


# Create a global manager for convenience
_global_manager = I18nManager("clitools")

def set_locale(locale_name: str) -> bool:
    """Set the current locale using the global manager."""
    return _global_manager.set_locale(locale_name)

def translate(text: str, **kwargs) -> str:
    """Translate text using the global manager."""
    return _global_manager.translate(text, **kwargs)

def get_available_locales() -> List[str]:
    """Get available locales from the global manager."""
    return _global_manager.get_available_locales()

def configure(app_name: str, **kwargs) -> None:
    """Configure the global i18n manager."""
    global _global_manager
    _global_manager = I18nManager(app_name, **kwargs)


# Shorthand alias for translate
_ = translate