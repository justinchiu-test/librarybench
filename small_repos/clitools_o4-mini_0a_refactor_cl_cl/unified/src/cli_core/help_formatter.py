"""
Custom help formatting for command-line interfaces.

This module provides enhanced help formatting for CLI applications.
"""

import argparse
import textwrap
from typing import List, Any, Optional, Dict


class ColoredHelpFormatter(argparse.HelpFormatter):
    """
    Custom help formatter with enhanced formatting and optional color support.
    """

    # ANSI color codes
    COLORS = {
        'blue': '\033[34m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'red': '\033[31m',
        'cyan': '\033[36m',
        'magenta': '\033[35m',
        'white': '\033[37m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }

    def __init__(self, prog, indent_increment=2, max_help_position=30, width=None,
                 color_enabled=True, theme=None):
        """
        Initialize the colored help formatter.

        Args:
            prog (str): The name of the program.
            indent_increment (int): Indentation increment.
            max_help_position (int): Maximum help position.
            width (int): Width of the output.
            color_enabled (bool): Whether to enable color output.
            theme (Dict[str, str]): Color theme mapping elements to color names.
        """
        super().__init__(prog, indent_increment, max_help_position, width)
        self.color_enabled = color_enabled
        self.theme = theme or {
            'program': 'bold',
            'command': 'green',
            'argument': 'cyan',
            'description': 'white',
            'heading': 'yellow'
        }

    def _apply_color(self, text, element_type):
        """
        Apply color to text based on element type and theme.

        Args:
            text (str): Text to format.
            element_type (str): Element type ('program', 'command', etc.).

        Returns:
            str: Formatted text.
        """
        if not self.color_enabled:
            return text

        color_name = self.theme.get(element_type)
        if not color_name or color_name not in self.COLORS:
            return text

        return f"{self.COLORS[color_name]}{text}{self.COLORS['reset']}"

    def format_help(self):
        """
        Format the entire help text with enhanced styling.

        Returns:
            str: Formatted help text.
        """
        help_text = super().format_help()

        # Apply colors to key elements
        if self.color_enabled:
            help_text = help_text.replace(
                f"usage: {self._prog}",
                f"usage: {self._apply_color(self._prog, 'program')}"
            )

            # Apply colors to section headings
            for heading in ["positional arguments", "optional arguments", "commands"]:
                help_text = help_text.replace(
                    heading,
                    self._apply_color(heading.upper(), 'heading')
                )

        return help_text

    def format_action(self, action):
        """
        Format a single action (argument or command) with enhanced styling.

        Args:
            action: The action to format.

        Returns:
            str: Formatted action.
        """
        # Format action as usual
        result = super().format_action(action)

        # Apply colors if enabled
        if self.color_enabled:
            # Color arguments
            if action.option_strings:
                for opt in action.option_strings:
                    result = result.replace(
                        opt,
                        self._apply_color(opt, 'argument')
                    )
            # Color positional arguments and commands
            elif hasattr(action, 'dest') and action.dest != 'help':
                result = result.replace(
                    action.dest,
                    self._apply_color(action.dest, 'command')
                )

        return result


def create_help_formatter(prog, color_enabled=True, theme=None):
    """
    Create a custom help formatter instance.

    Args:
        prog (str): Program name.
        color_enabled (bool): Whether to enable color output.
        theme (Dict[str, str]): Color theme.

    Returns:
        ColoredHelpFormatter: Configured help formatter.
    """
    return ColoredHelpFormatter(prog, color_enabled=color_enabled, theme=theme)


def format_help(help_dict, mode='color'):
    """
    Format help information into various output formats.

    Args:
        help_dict (Dict[str, str]): Dictionary mapping command names to descriptions.
        mode (str): Output format ('color', 'md', 'plain'). Default is 'color'.
            - 'color': ANSI-colored terminal output
            - 'md': Markdown output
            - 'plain': Plain text output

    Returns:
        str: Formatted help text.

    Raises:
        ValueError: If an invalid mode is specified.
    """
    if mode == 'md':
        # Format as markdown
        lines = ["# Command Help", ""]
        for cmd, desc in help_dict.items():
            lines.append(f"### `{cmd}`")
            lines.append("")
            lines.append(f"{desc}")
            lines.append("")
        return "\n".join(lines)

    elif mode == 'color':
        # Format with ANSI colors
        lines = ["\033[1mCOMMAND HELP\033[0m", ""]
        for cmd, desc in help_dict.items():
            # Blue for commands, reset for descriptions
            lines.append(f"\033[94m{cmd}\033[0m")
            lines.append(f"  {desc}")
            lines.append("")
        return "\n".join(lines)

    elif mode == 'plain':
        # Plain text formatting
        lines = ["COMMAND HELP", ""]
        for cmd, desc in help_dict.items():
            lines.append(f"{cmd}")
            lines.append(f"  {desc}")
            lines.append("")
        return "\n".join(lines)

    else:
        raise ValueError(f"Invalid help format mode: {mode}. Choose from 'color', 'md', or 'plain'.")