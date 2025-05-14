"""Adapter for translator.prompt_style."""

from typing import Dict, Any, Optional

class PromptStyle:
    """Style settings for prompts."""
    
    COLORS = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    
    def __init__(self, color_enabled: bool = True):
        """Initialize with color setting."""
        self.color_enabled = color_enabled
    
    def style_text(self, text: str, color: str = None) -> str:
        """Apply style to text."""
        if not self.color_enabled or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
    
    def info(self, text: str) -> str:
        """Style for info text."""
        return self.style_text(text, 'cyan')
    
    def warning(self, text: str) -> str:
        """Style for warning text."""
        return self.style_text(text, 'yellow')
    
    def error(self, text: str) -> str:
        """Style for error text."""
        return self.style_text(text, 'red')
    
    def success(self, text: str) -> str:
        """Style for success text."""
        return self.style_text(text, 'green')
