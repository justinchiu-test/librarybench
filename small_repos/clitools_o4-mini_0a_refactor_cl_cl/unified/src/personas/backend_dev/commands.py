"""
Backend developer commands.

Specialized commands for backend development workflows.
"""

from typing import Dict, Callable, List, Any

from ...cli_core.commands import CommandRegistry


def register_subcommands() -> Dict[str, Callable]:
    """
    Register backend developer specific subcommands.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    commands = {
        'migrate': lambda args: {'action': 'migrate'},
        'seed': lambda args: {'action': 'seed'},
        'status': lambda args: {'action': 'status'}
    }
    
    return commands


def setup_backend_commands(registry: CommandRegistry) -> None:
    """
    Set up backend developer commands in a command registry.
    
    Args:
        registry (CommandRegistry): Command registry to add commands to.
    """
    subcommands = register_subcommands()
    
    for name, handler in subcommands.items():
        registry.register(name, handler, help_text=f"{name} command for backend developers")
    
    # Add additional commands specific to backend development
    registry.register_with_args(
        'db', 
        lambda args: {'action': 'db', 'operation': getattr(args, 'operation', 'status')},
        args_config=[
            {
                'flags': ['operation'],
                'help': 'Database operation to perform',
                'choices': ['backup', 'restore', 'migrate', 'status'],
                'default': 'status'
            }
        ],
        help_text='Database management command'
    )
    
    registry.register_with_args(
        'deploy', 
        lambda args: {'action': 'deploy', 'env': getattr(args, 'env', 'staging')},
        args_config=[
            {
                'flags': ['--env'],
                'help': 'Environment to deploy to',
                'choices': ['dev', 'staging', 'production'],
                'default': 'staging'
            }
        ],
        help_text='Deploy application'
    )