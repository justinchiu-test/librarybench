def enable_accessibility_mode(renderer, mode=True):
    """
    Enable or disable accessibility mode on a renderer.
    """
    setattr(renderer, 'accessibility_mode', bool(mode))
    return renderer
