"""
CLI rendering systems for the CLI Form Library.
"""
import typing as t


class CursesRenderer:
    """
    Renderer for CLI forms using curses-like formatting.
    """
    
    def __init__(self, form_fields: t.Optional[t.Dict[str, t.Any]] = None):
        self.form_fields = form_fields or {}
        self.accessibility_mode = False
        self.locked_down = True
        self.screen = ""
        self.footer = "Press Tab to navigate, Enter to submit"
        
    def render(self, page_title: t.Optional[str] = None) -> str:
        """
        Render the form fields to a string representation.
        
        Args:
            page_title: Optional title for the current page
            
        Returns:
            A string representation of the rendered form
        """
        if self.accessibility_mode:
            output = ["ACCESSIBLE:"]
        else:
            output = []
            
        if page_title:
            output.append(f"--- {page_title} ---")
            
        # Render each field
        for field_id, field in self.form_fields.items():
            if hasattr(field, 'name') and hasattr(field, 'placeholder'):
                field_name = field.name
                placeholder = field.placeholder
                field_line = f"\t[{field_name}]({placeholder})"
                output.append(field_line)
                
        # Add footer
        output.append(self.footer)
        
        return "\n".join(output)
        
    def set_accessibility_mode(self, enabled: bool) -> None:
        """
        Enable or disable accessibility mode.
        
        Args:
            enabled: True to enable accessibility mode, False to disable it
        """
        self.accessibility_mode = enabled


# Global accessibility mode flag for the security officer implementation
_ACCESSIBILITY_MODE = False

# Reset the flag for tests
_ACCESSIBILITY_MODE = False

def is_accessibility_mode() -> bool:
    """Check if accessibility mode is enabled."""
    global _ACCESSIBILITY_MODE
    return _ACCESSIBILITY_MODE
    
def enable_accessibility_mode() -> bool:
    """Enable accessibility mode and return the new state."""
    global _ACCESSIBILITY_MODE
    _ACCESSIBILITY_MODE = True
    return _ACCESSIBILITY_MODE
    
def curses_renderer() -> dict:
    """Create and return a curses renderer in dict format."""
    return {
        "locked_down": True,
        "screen": "",
        "footer": "Press Tab to navigate, Enter to submit"
    }