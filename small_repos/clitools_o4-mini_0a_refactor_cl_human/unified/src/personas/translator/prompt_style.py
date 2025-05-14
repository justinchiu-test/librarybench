"""
Prompt styling module for translator tools.
Provides customizable ANSI styling for prompts and output.
"""

import sys
import os
from enum import Enum
from typing import Dict, List, Optional, Union


class Color(Enum):
    """ANSI color codes."""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    DEFAULT = 9


class Style(Enum):
    """ANSI style codes."""
    NORMAL = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    STRIKETHROUGH = 9


class PromptStyler:
    """
    ANSI terminal prompt styler.
    Provides colorful and stylized output for terminal applications.
    """
    
    def __init__(self, 
                enabled: Optional[bool] = None,
                theme: str = "default"):
        """
        Initialize a new prompt styler.
        
        Args:
            enabled: Whether styling is enabled (None for auto-detect)
            theme: Theme name to use
        """
        # Auto-detect if styling should be enabled
        if enabled is None:
            self.enabled = self._should_enable_styling()
        else:
            self.enabled = enabled
        
        # Set theme
        self.theme = theme
        self.theme_colors = self._get_theme_colors(theme)
    
    def style(self, 
             text: str, 
             fg: Optional[Union[Color, str, int]] = None, 
             bg: Optional[Union[Color, str, int]] = None, 
             styles: Optional[List[Union[Style, str, int]]] = None) -> str:
        """
        Apply ANSI styling to text.
        
        Args:
            text: Text to style
            fg: Foreground color
            bg: Background color
            styles: List of styles to apply
            
        Returns:
            Styled text
        """
        if not self.enabled:
            return text
        
        # Build ANSI code
        codes = []
        
        # Add styles
        if styles:
            for style in styles:
                style_code = self._get_style_code(style)
                if style_code is not None:
                    codes.append(str(style_code))
        
        # Add foreground color
        if fg is not None:
            fg_code = self._get_color_code(fg, True)
            if fg_code is not None:
                codes.append(str(fg_code))
        
        # Add background color
        if bg is not None:
            bg_code = self._get_color_code(bg, False)
            if bg_code is not None:
                codes.append(str(bg_code))
        
        # If no codes, return original text
        if not codes:
            return text
        
        # Build ANSI sequence
        ansi_seq = f"\033[{';'.join(codes)}m"
        reset_seq = "\033[0m"
        
        return f"{ansi_seq}{text}{reset_seq}"
    
    def theme_style(self, text: str, element: str) -> str:
        """
        Apply theme styling to text.
        
        Args:
            text: Text to style
            element: Theme element name
            
        Returns:
            Styled text
        """
        if not self.enabled or element not in self.theme_colors:
            return text
        
        theme_config = self.theme_colors[element]
        return self.style(
            text,
            fg=theme_config.get("fg"),
            bg=theme_config.get("bg"),
            styles=theme_config.get("styles")
        )
    
    def info(self, text: str) -> str:
        """Style text as information."""
        return self.theme_style(text, "info")
    
    def success(self, text: str) -> str:
        """Style text as success."""
        return self.theme_style(text, "success")
    
    def warning(self, text: str) -> str:
        """Style text as warning."""
        return self.theme_style(text, "warning")
    
    def error(self, text: str) -> str:
        """Style text as error."""
        return self.theme_style(text, "error")
    
    def prompt(self, text: str) -> str:
        """Style text as prompt."""
        return self.theme_style(text, "prompt")
    
    def header(self, text: str) -> str:
        """Style text as header."""
        return self.theme_style(text, "header")
    
    def disable(self) -> None:
        """Disable styling."""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable styling."""
        self.enabled = True
    
    def _should_enable_styling(self) -> bool:
        """
        Determine if ANSI styling should be enabled.
        
        Returns:
            True if styling should be enabled
        """
        # Check NO_COLOR environment variable
        if os.environ.get("NO_COLOR") is not None:
            return False
        
        # Check TERM environment variable
        term = os.environ.get("TERM", "")
        if term == "dumb":
            return False
        
        # Check if output is a TTY
        return sys.stdout.isatty()
    
    def _get_color_code(self, 
                       color: Union[Color, str, int], 
                       foreground: bool = True) -> Optional[int]:
        """
        Get ANSI color code.
        
        Args:
            color: Color to get code for
            foreground: Whether this is a foreground color
            
        Returns:
            ANSI color code
        """
        base = 30 if foreground else 40
        
        if isinstance(color, Color):
            return base + color.value
        elif isinstance(color, str):
            # Try to parse as Color enum
            try:
                return base + Color[color.upper()].value
            except KeyError:
                # Try to parse as number
                try:
                    return base + int(color)
                except ValueError:
                    return None
        elif isinstance(color, int):
            return base + color
        
        return None
    
    def _get_style_code(self, style: Union[Style, str, int]) -> Optional[int]:
        """
        Get ANSI style code.
        
        Args:
            style: Style to get code for
            
        Returns:
            ANSI style code
        """
        if isinstance(style, Style):
            return style.value
        elif isinstance(style, str):
            # Try to parse as Style enum
            try:
                return Style[style.upper()].value
            except KeyError:
                # Try to parse as number
                try:
                    return int(style)
                except ValueError:
                    return None
        elif isinstance(style, int):
            return style
        
        return None
    
    def _get_theme_colors(self, theme: str) -> Dict[str, Dict[str, any]]:
        """
        Get theme color configuration.
        
        Args:
            theme: Theme name
            
        Returns:
            Theme color configuration
        """
        # Default theme
        default_theme = {
            "info": {
                "fg": Color.BLUE,
                "styles": [Style.NORMAL]
            },
            "success": {
                "fg": Color.GREEN,
                "styles": [Style.NORMAL]
            },
            "warning": {
                "fg": Color.YELLOW,
                "styles": [Style.NORMAL]
            },
            "error": {
                "fg": Color.RED,
                "styles": [Style.BOLD]
            },
            "prompt": {
                "fg": Color.CYAN,
                "styles": [Style.BOLD]
            },
            "header": {
                "fg": Color.WHITE,
                "styles": [Style.BOLD]
            }
        }
        
        # Dark theme
        dark_theme = {
            "info": {
                "fg": Color.CYAN,
                "styles": [Style.NORMAL]
            },
            "success": {
                "fg": Color.GREEN,
                "styles": [Style.BOLD]
            },
            "warning": {
                "fg": Color.YELLOW,
                "styles": [Style.BOLD]
            },
            "error": {
                "fg": Color.RED,
                "styles": [Style.BOLD]
            },
            "prompt": {
                "fg": Color.MAGENTA,
                "styles": [Style.BOLD]
            },
            "header": {
                "fg": Color.WHITE,
                "bg": Color.BLUE,
                "styles": [Style.BOLD]
            }
        }
        
        # Light theme
        light_theme = {
            "info": {
                "fg": Color.BLUE,
                "styles": [Style.NORMAL]
            },
            "success": {
                "fg": Color.GREEN,
                "styles": [Style.NORMAL]
            },
            "warning": {
                "fg": Color.YELLOW,
                "styles": [Style.BOLD]
            },
            "error": {
                "fg": Color.RED,
                "styles": [Style.BOLD]
            },
            "prompt": {
                "fg": Color.MAGENTA,
                "styles": [Style.NORMAL]
            },
            "header": {
                "fg": Color.BLACK,
                "bg": Color.WHITE,
                "styles": [Style.BOLD]
            }
        }
        
        # Minimal theme
        minimal_theme = {
            "info": {
                "styles": [Style.NORMAL]
            },
            "success": {
                "styles": [Style.BOLD]
            },
            "warning": {
                "styles": [Style.UNDERLINE]
            },
            "error": {
                "styles": [Style.REVERSE]
            },
            "prompt": {
                "styles": [Style.BOLD]
            },
            "header": {
                "styles": [Style.BOLD, Style.UNDERLINE]
            }
        }
        
        # Available themes
        themes = {
            "default": default_theme,
            "dark": dark_theme,
            "light": light_theme,
            "minimal": minimal_theme
        }
        
        return themes.get(theme, default_theme)


# Create a global styler for convenience
_global_styler = PromptStyler()

def style(text: str, 
         fg: Optional[Union[Color, str, int]] = None, 
         bg: Optional[Union[Color, str, int]] = None, 
         styles: Optional[List[Union[Style, str, int]]] = None) -> str:
    """Style text using the global styler."""
    return _global_styler.style(text, fg, bg, styles)

def info(text: str) -> str:
    """Style text as information using the global styler."""
    return _global_styler.info(text)

def success(text: str) -> str:
    """Style text as success using the global styler."""
    return _global_styler.success(text)

def warning(text: str) -> str:
    """Style text as warning using the global styler."""
    return _global_styler.warning(text)

def error(text: str) -> str:
    """Style text as error using the global styler."""
    return _global_styler.error(text)

def prompt(text: str) -> str:
    """Style text as prompt using the global styler."""
    return _global_styler.prompt(text)

def header(text: str) -> str:
    """Style text as header using the global styler."""
    return _global_styler.header(text)

def disable() -> None:
    """Disable styling in the global styler."""
    _global_styler.disable()

def enable() -> None:
    """Enable styling in the global styler."""
    _global_styler.enable()

def configure(enabled: Optional[bool] = None, theme: str = "default") -> None:
    """Configure the global styler."""
    global _global_styler
    _global_styler = PromptStyler(enabled, theme)