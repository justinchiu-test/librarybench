"""
Error Handling for cli_form

This module provides error formatting and display utilities for form validation.
"""

import sys
from enum import Enum


class ErrorSeverity(Enum):
    """Enum representing different error severity levels."""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class ErrorFormatter:
    """Formats error messages with configurable styles."""
    
    # ANSI color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[31m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_red': '\033[41m',
        'bg_yellow': '\033[43m'
    }
    
    def __init__(self, use_colors=True, accessibility_mode=False):
        """
        Initialize error formatter.
        
        Args:
            use_colors (bool): Whether to use ANSI colors
            accessibility_mode (bool): Enable high-contrast, screen-reader friendly output
        """
        self.use_colors = use_colors and sys.stdout.isatty()
        self.accessibility_mode = accessibility_mode
        
    def format(self, message, severity=ErrorSeverity.ERROR, field=None):
        """
        Format an error message with appropriate styling.
        
        Args:
            message (str): Error message to format
            severity (ErrorSeverity): Error severity level
            field (str, optional): Field name associated with the error
            
        Returns:
            str: Formatted error message
        """
        # In accessibility mode, we don't use colors but add clear prefixes
        if self.accessibility_mode:
            prefix = f"[{severity.value.upper()}] "
            if field:
                return f"{prefix}{field}: {message}"
            return f"{prefix}{message}"
            
        # With colors enabled
        if self.use_colors:
            if severity == ErrorSeverity.ERROR:
                color = self.COLORS['red']
                bold = self.COLORS['bold']
            elif severity == ErrorSeverity.WARNING:
                color = self.COLORS['yellow']
                bold = ""
            elif severity == ErrorSeverity.CRITICAL:
                color = self.COLORS['bg_red'] + self.COLORS['white']
                bold = self.COLORS['bold']
            else:  # INFO
                color = self.COLORS['blue']
                bold = ""
                
            reset = self.COLORS['reset']
            
            if field:
                return f"{bold}{color}{field}: {message}{reset}"
            return f"{bold}{color}{message}{reset}"
        
        # Plain text formatting
        if field:
            return f"{field}: {message}"
        return message


def format_error(message, severity="error", field=None, use_colors=True, accessibility_mode=False):
    """
    Format an error message with the default error formatter.
    
    Args:
        message (str): Error message to format
        severity (str): Error severity ("info", "warning", "error", "critical")
        field (str, optional): Field name associated with the error
        use_colors (bool): Whether to use ANSI colors
        accessibility_mode (bool): Enable high-contrast, screen-reader friendly output
        
    Returns:
        str: Formatted error message
    """
    # Convert string severity to enum
    try:
        sev = ErrorSeverity(severity.lower())
    except (ValueError, AttributeError):
        sev = ErrorSeverity.ERROR
        
    formatter = ErrorFormatter(use_colors, accessibility_mode)
    return formatter.format(message, sev, field)