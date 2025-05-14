"""
Localization features for localization manager CLI.
"""

class LocalizationFeatures:
    """Localization features implementation."""
    
    def __init__(self):
        """Initialize localization features."""
        self.enabled = True
    
    def enable(self):
        """Enable localization features."""
        self.enabled = True
    
    def disable(self):
        """Disable localization features."""
        self.enabled = False