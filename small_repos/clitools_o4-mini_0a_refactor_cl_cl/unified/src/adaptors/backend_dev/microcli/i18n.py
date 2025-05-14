"""
Backend developer i18n adapter.

Provides backward compatibility for backend_dev.microcli.i18n.
"""

from typing import Dict

from ....cli_core.i18n import load_translations as core_load_translations


def load_translations(directory: str) -> Dict[str, Dict[str, str]]:
    """
    Load all translations from a directory.
    
    Args:
        directory (str): Directory path containing translation files.
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping file names to their translations.
    """
    return core_load_translations(directory)