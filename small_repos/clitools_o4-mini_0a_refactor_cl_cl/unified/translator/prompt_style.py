"""
Terminal prompt styling for translator CLI tools.
"""

from typing import Dict, Any, Optional


class PromptStyle:
    """Terminal styling utilities."""
    
    # ANSI color codes
    COLORS = {
        'black': '\033[30m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    @classmethod
    def style(cls, text: str, color: str) -> str:
        """
        Style text with the specified color.
        
        Args:
            text (str): Text to style.
            color (str): Color name.
            
        Returns:
            str: Styled text.
        """
        color_code = cls.COLORS.get(color.lower(), cls.COLORS['reset'])
        reset_code = cls.COLORS['reset']
        
        return f"{color_code}{text}{reset_code}"