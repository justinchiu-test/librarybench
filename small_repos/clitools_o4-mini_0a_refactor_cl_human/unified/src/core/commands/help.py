"""
Help formatter module for CLI tools.
Formats help text in different styles (plain, markdown, ANSI).
"""

import shutil
import textwrap
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..commands.registry import Command, CommandRegistry


class FormatStyle(Enum):
    """Available help formatting styles."""
    PLAIN = "plain"  # Plain text
    MARKDOWN = "markdown"  # Markdown for documentation
    ANSI = "ansi"  # ANSI colored terminal output


class HelpFormatter:
    """Formats help text for CLI commands."""
    
    def __init__(self, style: Union[FormatStyle, str] = FormatStyle.PLAIN):
        """
        Initialize a new help formatter.
        
        Args:
            style: Formatting style to use
        """
        if isinstance(style, str):
            try:
                self.style = FormatStyle(style.lower())
            except ValueError:
                self.style = FormatStyle.PLAIN
        else:
            self.style = style
        
        # Get terminal width if available
        self.width, _ = shutil.get_terminal_size((80, 20))
    
    def format_command(self, cmd: Command, include_subcommands: bool = True) -> str:
        """
        Format help for a command.
        
        Args:
            cmd: Command to format help for
            include_subcommands: Whether to include subcommands in output
            
        Returns:
            Formatted help text
        """
        if self.style == FormatStyle.MARKDOWN:
            return self._format_markdown(cmd, include_subcommands)
        elif self.style == FormatStyle.ANSI:
            return self._format_ansi(cmd, include_subcommands)
        else:
            return self._format_plain(cmd, include_subcommands)
    
    def format_command_registry(self, registry: CommandRegistry) -> str:
        """
        Format help for an entire command registry.
        
        Args:
            registry: CommandRegistry to format
            
        Returns:
            Formatted help text
        """
        return self.format_command(registry.root, True)
    
    def _format_plain(self, cmd: Command, include_subcommands: bool = True) -> str:
        """Format command help in plain text."""
        lines = []
        
        # Command name and description
        lines.append(f"COMMAND: {cmd.name}")
        if cmd.description:
            lines.append("")
            lines.append(cmd.description)
        
        # Detailed help
        if cmd.help_text:
            lines.append("")
            lines.append("DETAILS:")
            lines.append(self._wrap_text(cmd.help_text))
        
        # Arguments
        if cmd.arguments:
            lines.append("")
            lines.append("ARGUMENTS:")
            for arg in cmd.arguments:
                arg_str = f"  {arg['name']}"
                if not arg['required']:
                    default = arg['default']
                    default_str = str(default) if default is not None else 'None'
                    arg_str += f" (optional, default: {default_str})"
                lines.append(arg_str)
                if arg['help']:
                    lines.append(f"    {arg['help']}")
        
        # Subcommands
        if include_subcommands and cmd.subcommands:
            lines.append("")
            lines.append("SUBCOMMANDS:")
            for subcmd_name, subcmd in cmd.subcommands.items():
                lines.append(f"  {subcmd_name}: {subcmd.description}")
        
        return "\n".join(lines)
    
    def _format_markdown(self, cmd: Command, include_subcommands: bool = True) -> str:
        """Format command help in Markdown."""
        lines = []
        
        # Command name and description
        lines.append(f"# {cmd.name}")
        if cmd.description:
            lines.append("")
            lines.append(cmd.description)
        
        # Detailed help
        if cmd.help_text:
            lines.append("")
            lines.append("## Details")
            lines.append("")
            lines.append(cmd.help_text)
        
        # Arguments
        if cmd.arguments:
            lines.append("")
            lines.append("## Arguments")
            lines.append("")
            for arg in cmd.arguments:
                type_name = arg['type'].__name__ if hasattr(arg['type'], '__name__') else str(arg['type'])
                required = "Required" if arg['required'] else "Optional"
                default = arg['default'] if not arg['required'] else "N/A"
                
                lines.append(f"### `{arg['name']}`")
                lines.append("")
                lines.append(f"- **Type:** {type_name}")
                lines.append(f"- **{required}**")
                lines.append(f"- **Default:** {default}")
                
                if arg['help']:
                    lines.append("")
                    lines.append(arg['help'])
        
        # Subcommands
        if include_subcommands and cmd.subcommands:
            lines.append("")
            lines.append("## Subcommands")
            lines.append("")
            for subcmd_name, subcmd in cmd.subcommands.items():
                lines.append(f"### `{subcmd_name}`")
                lines.append("")
                lines.append(subcmd.description)
        
        return "\n".join(lines)
    
    def _format_ansi(self, cmd: Command, include_subcommands: bool = True) -> str:
        """Format command help with ANSI colors."""
        # ANSI color codes
        BOLD = "\033[1m"
        BLUE = "\033[34m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        RESET = "\033[0m"
        
        lines = []
        
        # Command name and description
        lines.append(f"{BOLD}{BLUE}COMMAND:{RESET} {BOLD}{cmd.name}{RESET}")
        if cmd.description:
            lines.append("")
            lines.append(cmd.description)
        
        # Detailed help
        if cmd.help_text:
            lines.append("")
            lines.append(f"{BOLD}DETAILS:{RESET}")
            lines.append(self._wrap_text(cmd.help_text))
        
        # Arguments
        if cmd.arguments:
            lines.append("")
            lines.append(f"{BOLD}ARGUMENTS:{RESET}")
            for arg in cmd.arguments:
                if arg['required']:
                    arg_name = f"{BOLD}{arg['name']}{RESET}"
                else:
                    arg_name = f"{arg['name']}"
                
                arg_str = f"  {arg_name}"
                if not arg['required']:
                    default = arg['default']
                    default_str = str(default) if default is not None else 'None'
                    arg_str += f" {YELLOW}(optional, default: {default_str}){RESET}"
                
                lines.append(arg_str)
                if arg['help']:
                    lines.append(f"    {arg['help']}")
        
        # Subcommands
        if include_subcommands and cmd.subcommands:
            lines.append("")
            lines.append(f"{BOLD}SUBCOMMANDS:{RESET}")
            for subcmd_name, subcmd in cmd.subcommands.items():
                lines.append(f"  {GREEN}{subcmd_name}{RESET}: {subcmd.description}")
        
        return "\n".join(lines)
    
    def _wrap_text(self, text: str, width: Optional[int] = None) -> str:
        """Wrap text to specified width."""
        wrap_width = width or self.width - 2
        wrapped_lines = []
        
        for line in text.split('\n'):
            if line.strip():
                wrapped_lines.extend(textwrap.wrap(line, width=wrap_width))
            else:
                wrapped_lines.append('')
                
        return '\n'.join(wrapped_lines)