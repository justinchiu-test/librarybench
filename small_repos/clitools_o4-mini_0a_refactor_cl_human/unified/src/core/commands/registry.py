"""
Command registry module for CLI tools.
Allows registration and organization of commands and subcommands.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class Command:
    """Represents a command in the CLI."""
    
    def __init__(self, 
                name: str, 
                callback: Callable,
                description: str = "",
                help_text: str = "",
                arguments: List[Dict[str, Any]] = None):
        """
        Initialize a new command.
        
        Args:
            name: Name of the command
            callback: Function to execute when command is invoked
            description: Short description of the command
            help_text: Detailed help text for the command
            arguments: List of argument definitions
        """
        self.name = name
        self.callback = callback
        self.description = description
        self.help_text = help_text
        self.arguments = arguments or []
        self.subcommands: Dict[str, 'Command'] = {}
    
    def add_subcommand(self, cmd: 'Command') -> None:
        """Add a subcommand to this command."""
        self.subcommands[cmd.name] = cmd
    
    def add_argument(self, 
                    name: str, 
                    type_: Any = str,
                    help_text: str = "",
                    required: bool = False,
                    default: Any = None) -> None:
        """
        Add an argument to the command.
        
        Args:
            name: Name of the argument
            type_: Expected type of the argument
            help_text: Help text for the argument
            required: Whether the argument is required
            default: Default value if not provided
        """
        self.arguments.append({
            'name': name,
            'type': type_,
            'help': help_text,
            'required': required,
            'default': default
        })
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the command with the given arguments."""
        return self.callback(*args, **kwargs)


class CommandRegistry:
    """Registry for CLI commands."""
    
    def __init__(self, name: str = "app"):
        """
        Initialize a new command registry.
        
        Args:
            name: Name of the root command/application
        """
        self.root = Command(name, lambda: None, f"{name} command line interface")
    
    def add_command(self, 
                   name: str, 
                   callback: Callable,
                   description: str = "",
                   help_text: str = "",
                   parent: Optional[str] = None) -> Command:
        """
        Register a new command.
        
        Args:
            name: Name of the command
            callback: Function to execute when command is invoked
            description: Short description of the command
            help_text: Detailed help text for the command
            parent: Parent command name (None for root)
            
        Returns:
            The created command object
        """
        cmd = Command(name, callback, description, help_text)
        
        # Auto-detect arguments from callback function
        sig = inspect.signature(callback)
        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
                
            required = param.default is inspect.Parameter.empty
            default = None if required else param.default
            
            cmd.add_argument(
                name=param_name,
                type_=param.annotation if param.annotation is not inspect.Parameter.empty else str,
                required=required,
                default=default
            )
        
        # Add to registry
        if parent is None:
            self.root.add_subcommand(cmd)
        else:
            parent_cmd = self.find_command(parent)
            if parent_cmd is None:
                raise ValueError(f"Parent command '{parent}' not found")
            parent_cmd.add_subcommand(cmd)
        
        return cmd
    
    def find_command(self, path: str) -> Optional[Command]:
        """
        Find a command by its path.
        
        Args:
            path: Command path (e.g., "parent:child")
            
        Returns:
            Command object or None if not found
        """
        parts = path.split(':')
        current = self.root
        
        for part in parts:
            if part in current.subcommands:
                current = current.subcommands[part]
            else:
                return None
        
        return current
    
    def get_command_tree(self) -> Dict[str, Any]:
        """
        Get a hierarchical representation of the command tree.
        
        Returns:
            Dictionary representing the command tree
        """
        
        def _build_tree(cmd: Command) -> Dict[str, Any]:
            result = {
                'name': cmd.name,
                'description': cmd.description,
                'help': cmd.help_text,
                'arguments': cmd.arguments,
            }
            
            if cmd.subcommands:
                result['subcommands'] = {
                    name: _build_tree(subcmd) 
                    for name, subcmd in cmd.subcommands.items()
                }
            
            return result
        
        return _build_tree(self.root)
    
    def execute_command(self, command_path: str, *args, **kwargs) -> Any:
        """
        Execute a command by its path.
        
        Args:
            command_path: Path to the command (e.g., "parent:child")
            *args: Positional arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command
            
        Returns:
            Result of command execution
        
        Raises:
            ValueError: If command not found
        """
        cmd = self.find_command(command_path)
        if cmd is None:
            raise ValueError(f"Command '{command_path}' not found")
        
        return cmd.execute(*args, **kwargs)


class CommandGroup:
    """
    Decorator-based interface for defining command groups.
    Similar to Flask's blueprints or Click's groups.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new command group.
        
        Args:
            name: Name of the command group
            description: Description of the group
        """
        self.name = name
        self.description = description
        self.commands: List[Tuple[str, Callable, Dict[str, Any]]] = []
    
    def command(self, name: Optional[str] = None, **attrs):
        """
        Decorator to register a command in this group.
        
        Args:
            name: Name of the command (defaults to function name)
            **attrs: Additional command attributes
            
        Returns:
            Decorator function
        """
        def decorator(f):
            cmd_name = name or f.__name__
            self.commands.append((cmd_name, f, attrs))
            return f
        return decorator
    
    def register_with(self, registry: CommandRegistry) -> None:
        """
        Register all commands in this group with a registry.
        
        Args:
            registry: CommandRegistry to register with
        """
        for name, func, attrs in self.commands:
            description = attrs.get('description', '')
            help_text = attrs.get('help', '')
            
            registry.add_command(
                name=name,
                callback=func,
                description=description,
                help_text=help_text,
                parent=self.name
            )