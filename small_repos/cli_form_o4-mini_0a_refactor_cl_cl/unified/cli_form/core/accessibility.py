"""
Accessibility features for the CLI Form Library.
"""
import typing as t

# Global accessibility mode flag
ACCESSIBILITY_MODE = False


def enable_accessibility_mode(renderer=None, enabled: bool = True) -> bool:
    """
    Enable accessibility mode globally or for a specific renderer.
    
    Args:
        renderer: Optional renderer object to configure
        enabled: True to enable, False to disable
        
    Returns:
        The new accessibility mode state
    """
    global ACCESSIBILITY_MODE
    
    # Update global flag
    ACCESSIBILITY_MODE = enabled
    
    # Update renderer if provided
    if renderer is not None:
        if hasattr(renderer, 'accessibility_mode'):
            renderer.accessibility_mode = enabled
        elif hasattr(renderer, 'set_accessibility_mode'):
            renderer.set_accessibility_mode(enabled)
            
    return ACCESSIBILITY_MODE