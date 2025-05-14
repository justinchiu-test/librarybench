"""
Localization manager commands.

Specialized commands for managing localization workflows.
"""

from typing import Dict, Callable, List, Any

from ...cli_core.commands import CommandRegistry


def register_localization_commands() -> Dict[str, Callable]:
    """
    Register localization manager specific commands.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    commands = {
        'scan': lambda args: {
            'action': 'scan',
            'directory': getattr(args, 'directory', '.'),
            'pattern': getattr(args, 'pattern', '*.py')
        },
        'generate': lambda args: {
            'action': 'generate',
            'locale': getattr(args, 'locale', None),
            'template': getattr(args, 'template', None)
        },
        'status': lambda args: {
            'action': 'status',
            'locale': getattr(args, 'locale', None)
        },
        'export': lambda args: {
            'action': 'export',
            'locale': getattr(args, 'locale', None),
            'format': getattr(args, 'format', 'po')
        },
        'import': lambda args: {
            'action': 'import',
            'file': getattr(args, 'file', None),
            'locale': getattr(args, 'locale', None)
        }
    }
    
    return commands


def setup_localization_commands(registry: CommandRegistry) -> None:
    """
    Set up localization manager commands in a command registry.
    
    Args:
        registry (CommandRegistry): Command registry to add commands to.
    """
    commands = register_localization_commands()
    
    registry.register_with_args(
        'scan',
        commands['scan'],
        args_config=[
            {
                'flags': ['--directory', '-d'],
                'help': 'Directory to scan',
                'default': '.'
            },
            {
                'flags': ['--pattern', '-p'],
                'help': 'File pattern to scan',
                'default': '*.py'
            },
            {
                'flags': ['--recursive', '-r'],
                'help': 'Scan recursively',
                'action': 'store_true'
            },
            {
                'flags': ['--output', '-o'],
                'help': 'Output template file',
                'default': 'messages.pot'
            }
        ],
        help_text='Scan source files for translatable strings'
    )
    
    registry.register_with_args(
        'generate',
        commands['generate'],
        args_config=[
            {
                'flags': ['locale'],
                'help': 'Locale to generate',
                'required': True
            },
            {
                'flags': ['--template', '-t'],
                'help': 'Template file',
                'default': 'messages.pot'
            },
            {
                'flags': ['--output-dir', '-o'],
                'help': 'Output directory',
                'default': 'locales'
            }
        ],
        help_text='Generate translation files for a locale'
    )
    
    registry.register_with_args(
        'status',
        commands['status'],
        args_config=[
            {
                'flags': ['--locale', '-l'],
                'help': 'Locale to check'
            },
            {
                'flags': ['--format', '-f'],
                'help': 'Output format',
                'choices': ['text', 'json', 'csv'],
                'default': 'text'
            }
        ],
        help_text='Show translation status'
    )
    
    registry.register_with_args(
        'export',
        commands['export'],
        args_config=[
            {
                'flags': ['locale'],
                'help': 'Locale to export',
                'required': True
            },
            {
                'flags': ['--format', '-f'],
                'help': 'Export format',
                'choices': ['po', 'mo', 'json', 'csv', 'xlsx'],
                'default': 'po'
            },
            {
                'flags': ['--output', '-o'],
                'help': 'Output file'
            }
        ],
        help_text='Export translations'
    )
    
    registry.register_with_args(
        'import',
        commands['import'],
        args_config=[
            {
                'flags': ['file'],
                'help': 'File to import',
                'required': True
            },
            {
                'flags': ['--locale', '-l'],
                'help': 'Target locale',
                'required': True
            },
            {
                'flags': ['--merge'],
                'help': 'Merge with existing translations',
                'action': 'store_true'
            }
        ],
        help_text='Import translations'
    )
    
    registry.register_with_args(
        'compile',
        lambda args: {'action': 'compile', 'locale': getattr(args, 'locale', None)},
        args_config=[
            {
                'flags': ['--locale', '-l'],
                'help': 'Locale to compile',
                'required': True
            },
            {
                'flags': ['--output-dir', '-o'],
                'help': 'Output directory',
                'default': 'compiled'
            }
        ],
        help_text='Compile translations to binary format'
    )