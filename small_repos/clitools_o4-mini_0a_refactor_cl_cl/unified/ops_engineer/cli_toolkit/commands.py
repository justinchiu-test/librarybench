"""
Command handling for operations engineer CLI tools.
"""

from typing import Dict, Any, Callable, Optional, List


class CommandGroup:
    """Command group for organizing CLI commands."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a command group.
        
        Args:
            name (str): Group name.
            description (str): Group description.
        """
        self.name = name
        self.description = description
        self.commands: Dict[str, Callable] = {}
    
    def add_command(self, name: str, callback: Callable) -> None:
        """
        Add a command to the group.
        
        Args:
            name (str): Command name.
            callback (Callable): Command implementation.
        """
        self.commands[name] = callback


class CLI:
    """CLI application with command grouping."""
    
    def __init__(self, name: str = "app", description: str = ""):
        """
        Initialize a CLI application.
        
        Args:
            name (str): Application name.
            description (str): Application description.
        """
        self.name = name
        self.description = description
        self.groups: Dict[str, CommandGroup] = {}
    
    def register_group(self, name: str, description: str = "") -> CommandGroup:
        """
        Register a command group.
        
        Args:
            name (str): Group name.
            description (str): Group description.
            
        Returns:
            CommandGroup: The created command group.
        """
        group = CommandGroup(name, description)
        self.groups[name] = group
        return group
    
    def register_command(self, group_name: str, command_name: str, 
                        callback: Callable) -> None:
        """
        Register a command within a group.
        
        Args:
            group_name (str): Group name.
            command_name (str): Command name.
            callback (Callable): Command implementation.
            
        Raises:
            KeyError: If group does not exist.
        """
        if group_name not in self.groups:
            self.register_group(group_name)
        
        self.groups[group_name].add_command(command_name, callback)
    
    def run(self, args: Optional[List[str]] = None) -> Any:
        """
        Run the CLI with the given arguments.
        
        Args:
            args (List[str], optional): Command line arguments.
            
        Returns:
            Any: Result of the executed command.
            
        Raises:
            ValueError: If command not found.
        """
        # Mock implementation for testing
        if not args or len(args) < 2:
            return self._print_help()
        
        group_name = args[0]
        command_name = args[1]
        
        if group_name not in self.groups:
            raise ValueError(f"Group not found: {group_name}")
        
        group = self.groups[group_name]
        
        if command_name not in group.commands:
            raise ValueError(f"Command not found: {group_name} {command_name}")
        
        command = group.commands[command_name]
        return command()
    
    def _print_help(self) -> str:
        """
        Print help information.
        
        Returns:
            str: Help text.
        """
        help_text = [f"{self.name} - {self.description}"]
        
        for group_name, group in self.groups.items():
            help_text.append(f"\n{group_name} commands:")
            for cmd_name in group.commands:
                help_text.append(f"  {group_name} {cmd_name}")
        
        return "\n".join(help_text)