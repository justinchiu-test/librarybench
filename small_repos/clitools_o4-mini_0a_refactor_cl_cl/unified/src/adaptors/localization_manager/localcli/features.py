"""
Localization manager features adapter.

Provides backward compatibility for localization_manager.localcli.features.
"""

from typing import Dict, Any

from src.personas.localization_manager.commands import register_localization_commands


def get_features() -> Dict[str, Any]:
    """
    Get available localization features.
    
    Returns:
        Dict[str, Any]: Dictionary of available features.
    """
    commands = register_localization_commands()
    
    return {
        'scan': {
            'description': 'Scan source files for translatable strings',
            'enabled': True
        },
        'generate': {
            'description': 'Generate translation files for a locale',
            'enabled': True
        },
        'status': {
            'description': 'Show translation status',
            'enabled': True
        },
        'export': {
            'description': 'Export translations',
            'enabled': True
        },
        'import': {
            'description': 'Import translations',
            'enabled': True
        },
        'compile': {
            'description': 'Compile translations to binary format',
            'enabled': True
        }
    }