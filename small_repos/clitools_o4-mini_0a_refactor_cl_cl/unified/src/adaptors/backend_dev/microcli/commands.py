"""
Backend developer command adapter.

Provides backward compatibility for backend_dev.microcli.commands.
"""

from typing import Dict, Callable

from ....personas.backend_dev.commands import register_subcommands as core_register_subcommands


def register_subcommands() -> Dict[str, Callable]:
    """
    Register backend developer specific subcommands.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    return core_register_subcommands()