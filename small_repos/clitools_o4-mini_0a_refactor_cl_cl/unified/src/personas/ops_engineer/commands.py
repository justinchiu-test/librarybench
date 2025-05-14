"""
Operations engineer commands.

Specialized commands for infrastructure and operations workflows.
"""

from typing import Dict, Callable, List, Any

from ...cli_core.commands import CommandRegistry


def register_ops_commands() -> Dict[str, Callable]:
    """
    Register operations engineer specific commands.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    commands = {
        'deploy': lambda args: {'action': 'deploy', 'environment': getattr(args, 'environment', 'staging')},
        'rollback': lambda args: {'action': 'rollback', 'version': getattr(args, 'version', None)},
        'scale': lambda args: {'action': 'scale', 'service': getattr(args, 'service', None), 'replicas': getattr(args, 'replicas', 1)},
        'monitor': lambda args: {'action': 'monitor', 'service': getattr(args, 'service', None)},
        'config': lambda args: {'action': 'config', 'operation': getattr(args, 'operation', 'get')}
    }
    
    return commands


def setup_ops_commands(registry: CommandRegistry) -> None:
    """
    Set up operations engineer commands in a command registry.
    
    Args:
        registry (CommandRegistry): Command registry to add commands to.
    """
    commands = register_ops_commands()
    
    registry.register_with_args(
        'deploy',
        commands['deploy'],
        args_config=[
            {
                'flags': ['--environment', '-e'],
                'help': 'Environment to deploy to',
                'choices': ['dev', 'staging', 'production'],
                'default': 'staging'
            },
            {
                'flags': ['--version', '-v'],
                'help': 'Version to deploy',
                'default': 'latest'
            }
        ],
        help_text='Deploy application to environment'
    )
    
    registry.register_with_args(
        'rollback',
        commands['rollback'],
        args_config=[
            {
                'flags': ['--version', '-v'],
                'help': 'Version to rollback to',
                'required': True
            },
            {
                'flags': ['--environment', '-e'],
                'help': 'Environment to rollback in',
                'default': 'staging'
            }
        ],
        help_text='Rollback to a previous version'
    )
    
    registry.register_with_args(
        'scale',
        commands['scale'],
        args_config=[
            {
                'flags': ['service'],
                'help': 'Service to scale',
                'required': True
            },
            {
                'flags': ['--replicas', '-r'],
                'help': 'Number of replicas',
                'type': int,
                'default': 1
            }
        ],
        help_text='Scale a service'
    )
    
    registry.register_with_args(
        'monitor',
        commands['monitor'],
        args_config=[
            {
                'flags': ['service'],
                'help': 'Service to monitor',
                'nargs': '?'
            },
            {
                'flags': ['--log-level'],
                'help': 'Log level to filter by',
                'choices': ['debug', 'info', 'warning', 'error', 'critical'],
                'default': 'info'
            }
        ],
        help_text='Monitor service logs and metrics'
    )
    
    registry.register_with_args(
        'config',
        commands['config'],
        args_config=[
            {
                'flags': ['operation'],
                'help': 'Configuration operation',
                'choices': ['get', 'set', 'list', 'diff'],
                'default': 'get'
            },
            {
                'flags': ['--key'],
                'help': 'Configuration key'
            },
            {
                'flags': ['--value'],
                'help': 'Configuration value (for set operation)'
            },
            {
                'flags': ['--environment', '-e'],
                'help': 'Environment',
                'default': 'current'
            }
        ],
        help_text='Manage application configuration'
    )