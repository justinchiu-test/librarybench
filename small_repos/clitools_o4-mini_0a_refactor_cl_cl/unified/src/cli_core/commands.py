"""
Core command handling for CLI applications.

This module provides functionality for command registration, execution, and argument parsing.
"""

import argparse
import os
import sys
from typing import Dict, Callable, List, Any, Optional, Union

class CommandRegistry:
    """
    Registry for CLI commands.
    
    Manages command registration and execution with argument parsing.
    """
    
    def __init__(self, program_name=None, description=None):
        """
        Initialize the command registry.
        
        Args:
            program_name (str): Name of the CLI program.
            description (str): Description of the CLI program.
        """
        self.program_name = program_name or os.path.basename(sys.argv[0])
        self.description = description
        self.commands: Dict[str, Callable] = {}
        self.parent_parser = argparse.ArgumentParser(add_help=False)
        self.parser = argparse.ArgumentParser(
            prog=self.program_name,
            description=self.description,
            parents=[self.parent_parser]
        )
        self.subparsers = self.parser.add_subparsers(dest='command')
        
        # Add version flag support
        self.parent_parser.add_argument('--version', action='store_true', 
                                        help='Show version information')
    
    def register(self, name: str, handler: Callable, help_text: str = None) -> None:
        """
        Register a command.
        
        Args:
            name (str): Name of the command.
            handler (Callable): Function to handle the command.
            help_text (str): Help text for the command.
        """
        self.commands[name] = handler
        self.subparsers.add_parser(name, help=help_text)
    
    def register_with_args(self, name: str, handler: Callable, 
                          args_config: List[Dict[str, Any]] = None, 
                          help_text: str = None) -> None:
        """
        Register a command with argument configuration.
        
        Args:
            name (str): Name of the command.
            handler (Callable): Function to handle the command.
            args_config (List[Dict]): List of argument configurations.
            help_text (str): Help text for the command.
        """
        self.commands[name] = handler
        subparser = self.subparsers.add_parser(name, help=help_text)
        
        if args_config:
            for arg_config in args_config:
                flags = arg_config.pop('flags')
                subparser.add_argument(*flags, **arg_config)
    
    def execute(self, args: List[str] = None) -> Any:
        """
        Parse arguments and execute the appropriate command.
        
        Args:
            args (List[str]): Command-line arguments to parse. If None, use sys.argv[1:].
            
        Returns:
            The result of the executed command or None.
        """
        args = args or sys.argv[1:]
        parsed_args = self.parser.parse_args(args)
        
        # Handle version flag
        if hasattr(parsed_args, 'version') and parsed_args.version:
            version = self._get_version()
            print(version)
            return version
        
        # Execute command if available
        if parsed_args.command and parsed_args.command in self.commands:
            return self.commands[parsed_args.command](parsed_args)
        elif not args:
            self.parser.print_help()
        
        return None
    
    def _get_version(self) -> str:
        """
        Get version information from version.txt if available.
        
        Returns:
            str: Version string or "unknown".
        """
        try:
            with open('version.txt', 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, IOError):
            return "unknown"


def create_registry(program_name=None, description=None) -> CommandRegistry:
    """
    Create a new command registry.
    
    Args:
        program_name (str): Name of the CLI program.
        description (str): Description of the CLI program.
        
    Returns:
        CommandRegistry: Initialized command registry.
    """
    return CommandRegistry(program_name, description)


def register_subcommands() -> Dict[str, Callable]:
    """
    Register default subcommands.
    
    This is a placeholder implementation that can be extended by persona-specific code.
    
    Returns:
        Dict[str, Callable]: Dictionary of registered commands.
    """
    return {}