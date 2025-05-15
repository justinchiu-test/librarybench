"""
Accessibility Features for cli_form

This module provides accessibility enhancements for making forms usable
with screen readers and other assistive technologies.
"""

import os
import sys


class AccessibilityMode:
    """Manages accessibility settings for forms."""
    
    def __init__(self):
        """Initialize with default accessibility settings."""
        self.enabled = False
        self.screen_reader_support = False
        self.high_contrast = False
        self.large_text = False
        self.simplified_navigation = False
        self.keyboard_only = True
        self.reduced_motion = False
        
    def enable(self, screen_reader=True, high_contrast=True, large_text=False,
               simplified_nav=True, keyboard_only=True, reduced_motion=False):
        """
        Enable accessibility mode with specific features.
        
        Args:
            screen_reader (bool): Optimize for screen readers
            high_contrast (bool): Use high contrast text
            large_text (bool): Use larger text
            simplified_nav (bool): Simplify navigation
            keyboard_only (bool): Enable keyboard-only navigation
            reduced_motion (bool): Reduce or eliminate animations
            
        Returns:
            AccessibilityMode: self for chaining
        """
        self.enabled = True
        self.screen_reader_support = screen_reader
        self.high_contrast = high_contrast
        self.large_text = large_text
        self.simplified_navigation = simplified_nav
        self.keyboard_only = keyboard_only
        self.reduced_motion = reduced_motion
        
        # Set environment variable to inform other components
        os.environ['CLI_FORM_ACCESSIBILITY'] = '1'
        
        return self
        
    def disable(self):
        """
        Disable accessibility mode.
        
        Returns:
            AccessibilityMode: self for chaining
        """
        self.enabled = False
        
        # Clear environment variable
        if 'CLI_FORM_ACCESSIBILITY' in os.environ:
            del os.environ['CLI_FORM_ACCESSIBILITY']
            
        return self
    
    def is_enabled(self):
        """
        Check if accessibility mode is enabled.
        
        Returns:
            bool: True if enabled
        """
        return self.enabled or os.environ.get('CLI_FORM_ACCESSIBILITY') == '1'
    
    def get_settings(self):
        """
        Get all accessibility settings.
        
        Returns:
            dict: Dictionary of all settings
        """
        return {
            'enabled': self.is_enabled(),
            'screen_reader_support': self.screen_reader_support,
            'high_contrast': self.high_contrast,
            'large_text': self.large_text,
            'simplified_navigation': self.simplified_navigation,
            'keyboard_only': self.keyboard_only,
            'reduced_motion': self.reduced_motion
        }
    
    def describe(self):
        """
        Get a human-readable description of enabled accessibility features.
        
        Returns:
            str: Description of enabled features
        """
        if not self.is_enabled():
            return "Accessibility mode is disabled"
            
        features = []
        
        if self.screen_reader_support:
            features.append("Screen reader support")
        if self.high_contrast:
            features.append("High contrast text")
        if self.large_text:
            features.append("Large text")
        if self.simplified_navigation:
            features.append("Simplified navigation")
        if self.keyboard_only:
            features.append("Keyboard-only navigation")
        if self.reduced_motion:
            features.append("Reduced motion")
            
        return "Accessibility mode enabled with: " + ", ".join(features)


# Global accessibility mode instance
_accessibility_mode = AccessibilityMode()


def enable_accessibility_mode(screen_reader=True, high_contrast=True, large_text=False,
                            simplified_nav=True, keyboard_only=True, reduced_motion=False):
    """
    Enable accessibility mode globally.
    
    Args:
        screen_reader (bool): Optimize for screen readers
        high_contrast (bool): Use high contrast text
        large_text (bool): Use larger text
        simplified_nav (bool): Simplify navigation
        keyboard_only (bool): Enable keyboard-only navigation
        reduced_motion (bool): Reduce or eliminate animations
        
    Returns:
        dict: The current accessibility settings
    """
    global _accessibility_mode
    _accessibility_mode.enable(
        screen_reader, high_contrast, large_text,
        simplified_nav, keyboard_only, reduced_motion
    )
    return _accessibility_mode.get_settings()


def disable_accessibility_mode():
    """
    Disable accessibility mode globally.
    
    Returns:
        dict: The current accessibility settings
    """
    global _accessibility_mode
    _accessibility_mode.disable()
    return _accessibility_mode.get_settings()


def get_accessibility_settings():
    """
    Get current accessibility settings.
    
    Returns:
        dict: The current accessibility settings
    """
    global _accessibility_mode
    return _accessibility_mode.get_settings()


def is_accessibility_mode_enabled():
    """
    Check if accessibility mode is enabled.
    
    Returns:
        bool: True if enabled
    """
    global _accessibility_mode
    return _accessibility_mode.is_enabled()