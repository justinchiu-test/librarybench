"""
Help formatter for the Data Pipeline CLI.
"""
import textwrap
from typing import Dict, List, Optional, Tuple, Any

def format_help(commands: Dict[str, str], mode: str = 'plain') -> str:
    """
    Format help text for commands.
    
    Args:
        commands: Dictionary of command names to descriptions
        mode: Formatting mode ('plain', 'md', 'color')
        
    Returns:
        Formatted help text
        
    Raises:
        ValueError: If mode is invalid
    """
    if mode == 'plain':
        return _format_plain(commands)
    elif mode == 'md':
        return _format_markdown(commands)
    elif mode == 'color':
        return _format_color(commands)
    else:
        raise ValueError(f"Invalid formatting mode: {mode}")

def _format_plain(commands: Dict[str, str]) -> str:
    """Format help text as plain text."""
    lines = []
    for cmd, desc in commands.items():
        lines.append(f"{cmd}: {desc}")
    return "\n".join(lines)

def _format_markdown(commands: Dict[str, str]) -> str:
    """Format help text as Markdown."""
    lines = []
    for cmd, desc in commands.items():
        lines.append(f"### `{cmd}`")
        lines.append("")
        lines.append(desc)
        lines.append("")
    return "\n".join(lines)

def _format_color(commands: Dict[str, str]) -> str:
    """Format help text with ANSI color codes."""
    lines = []
    for cmd, desc in commands.items():
        lines.append(f"\033[94m{cmd}\033[0m: {desc}")
    return "\n".join(lines)

class HelpFormatter:
    """
    Formats help text for CLI commands.
    """
    
    def __init__(self, 
                width: int = 80, 
                indent: int = 2, 
                color: bool = True):
        """
        Initialize a new help formatter.
        
        Args:
            width: Maximum width of help text
            indent: Number of spaces to indent
            color: Whether to use color in output
        """
        self.width = width
        self.indent = indent
        self.color = color
    
    def format_command(self, 
                      name: str, 
                      description: str, 
                      usage: str, 
                      options: List[Dict[str, str]]) -> str:
        """
        Format help text for a command.
        
        Args:
            name: Command name
            description: Command description
            usage: Command usage
            options: List of option dictionaries with 'name', 'description', and optional 'default'
            
        Returns:
            Formatted help text
        """
        parts = []
        
        # Add header
        parts.append(self._format_header(name))
        parts.append("")
        
        # Add description
        parts.append(self._format_description(description))
        parts.append("")
        
        # Add usage
        parts.append(self._format_usage(usage))
        parts.append("")
        
        # Add options
        if options:
            parts.append(self._format_options_header())
            for option in options:
                parts.append(self._format_option(option))
            parts.append("")
        
        return "\n".join(parts)
    
    def format_commands(self, 
                       title: str, 
                       commands: Dict[str, str]) -> str:
        """
        Format a list of commands.
        
        Args:
            title: Section title
            commands: Dictionary of command names to descriptions
            
        Returns:
            Formatted commands list
        """
        parts = []
        
        # Add header
        parts.append(self._format_section_header(title))
        parts.append("")
        
        # Add commands
        max_name_len = max(len(name) for name in commands.keys()) if commands else 0
        
        for name, description in commands.items():
            indent_str = " " * self.indent
            padding = " " * (max_name_len - len(name) + 2)
            
            # Wrap description
            desc_width = self.width - self.indent - max_name_len - 2
            wrapped_desc = textwrap.fill(
                description, 
                width=desc_width,
                initial_indent="",
                subsequent_indent=" " * (self.indent + max_name_len + 2)
            )
            
            # Format command
            if self.color:
                name_str = f"\033[1m{name}\033[0m"
            else:
                name_str = name
                
            parts.append(f"{indent_str}{name_str}{padding}{wrapped_desc}")
        
        parts.append("")
        return "\n".join(parts)
    
    def _format_header(self, text: str) -> str:
        """Format a header."""
        if self.color:
            return f"\033[1;36m{text}\033[0m"
        return text
    
    def _format_section_header(self, text: str) -> str:
        """Format a section header."""
        if self.color:
            return f"\033[1;33m{text}\033[0m"
        return text
    
    def _format_description(self, text: str) -> str:
        """Format a description."""
        indent_str = " " * self.indent
        
        # Wrap text
        wrapped = textwrap.fill(
            text, 
            width=self.width - self.indent,
            initial_indent=indent_str,
            subsequent_indent=indent_str
        )
        
        return wrapped
    
    def _format_usage(self, text: str) -> str:
        """Format usage text."""
        indent_str = " " * self.indent
        
        if self.color:
            header = f"\033[1;33mUsage:\033[0m"
        else:
            header = "Usage:"
            
        wrapped = textwrap.fill(
            text, 
            width=self.width - self.indent,
            initial_indent=f"{indent_str}{header} ",
            subsequent_indent=indent_str + "       "
        )
        
        return wrapped
    
    def _format_options_header(self) -> str:
        """Format options header."""
        indent_str = " " * self.indent
        
        if self.color:
            return f"{indent_str}\033[1;33mOptions:\033[0m"
        return f"{indent_str}Options:"
    
    def _format_option(self, option: Dict[str, str]) -> str:
        """Format an option."""
        name = option.get("name", "")
        description = option.get("description", "")
        default = option.get("default")
        
        # Add default value to description if provided
        if default is not None:
            description = f"{description} (default: {default})"
        
        # Double indent for options
        indent_str = " " * (self.indent * 2)
        
        # Wrap description
        desc_width = self.width - (self.indent * 2) - 4  # 4 for name padding
        wrapped_desc = textwrap.fill(
            description, 
            width=desc_width,
            initial_indent="",
            subsequent_indent=" " * ((self.indent * 2) + 4)
        )
        
        # Format option
        if self.color:
            name_str = f"\033[1m{name}\033[0m"
        else:
            name_str = name
            
        return f"{indent_str}{name_str}    {wrapped_desc}"