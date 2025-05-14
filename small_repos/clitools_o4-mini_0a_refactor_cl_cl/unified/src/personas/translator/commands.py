"""
Translator commands.

Specialized commands for translation workflows.
"""

import os
from typing import Dict, Callable, List, Any

from ...cli_core.commands import CommandRegistry


def register_translator_commands() -> Dict[str, Callable]:
    """
    Register translator specific commands.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    commands = {
        'translate': lambda args: {
            'action': 'translate', 
            'source': getattr(args, 'source', None),
            'target': getattr(args, 'target', None),
            'text': getattr(args, 'text', None)
        },
        'extract': lambda args: {
            'action': 'extract',
            'file': getattr(args, 'file', None),
            'format': getattr(args, 'format', 'po')
        },
        'validate': lambda args: {
            'action': 'validate',
            'file': getattr(args, 'file', None)
        },
        'merge': lambda args: {
            'action': 'merge',
            'source': getattr(args, 'source', None),
            'target': getattr(args, 'target', None)
        }
    }
    
    return commands


def setup_translator_commands(registry: CommandRegistry) -> None:
    """
    Set up translator commands in a command registry.
    
    Args:
        registry (CommandRegistry): Command registry to add commands to.
    """
    commands = register_translator_commands()
    
    registry.register_with_args(
        'translate',
        commands['translate'],
        args_config=[
            {
                'flags': ['--source', '-s'],
                'help': 'Source language',
                'required': True
            },
            {
                'flags': ['--target', '-t'],
                'help': 'Target language',
                'required': True
            },
            {
                'flags': ['--text'],
                'help': 'Text to translate'
            },
            {
                'flags': ['--file', '-f'],
                'help': 'File to translate'
            },
            {
                'flags': ['--glossary'],
                'help': 'Glossary to use'
            }
        ],
        help_text='Translate text or file'
    )
    
    registry.register_with_args(
        'extract',
        commands['extract'],
        args_config=[
            {
                'flags': ['file'],
                'help': 'File to extract strings from',
                'required': True
            },
            {
                'flags': ['--format'],
                'help': 'Output format',
                'choices': ['po', 'json', 'yaml', 'csv'],
                'default': 'po'
            },
            {
                'flags': ['--output', '-o'],
                'help': 'Output file',
                'default': 'messages.po'
            }
        ],
        help_text='Extract translatable strings'
    )
    
    registry.register_with_args(
        'validate',
        commands['validate'],
        args_config=[
            {
                'flags': ['file'],
                'help': 'Translation file to validate',
                'required': True
            },
            {
                'flags': ['--strict'],
                'help': 'Enable strict validation',
                'action': 'store_true'
            }
        ],
        help_text='Validate translation file'
    )
    
    registry.register_with_args(
        'merge',
        commands['merge'],
        args_config=[
            {
                'flags': ['--source', '-s'],
                'help': 'Source translation file',
                'required': True
            },
            {
                'flags': ['--target', '-t'],
                'help': 'Target translation file',
                'required': True
            },
            {
                'flags': ['--output', '-o'],
                'help': 'Output file',
                'default': 'merged.po'
            }
        ],
        help_text='Merge translation files'
    )
    
    registry.register_with_args(
        'stats',
        lambda args: {'action': 'stats', 'file': getattr(args, 'file', None)},
        args_config=[
            {
                'flags': ['file'],
                'help': 'Translation file to analyze',
                'required': True
            },
            {
                'flags': ['--format'],
                'help': 'Output format',
                'choices': ['text', 'json', 'csv'],
                'default': 'text'
            }
        ],
        help_text='Show translation statistics'
    )