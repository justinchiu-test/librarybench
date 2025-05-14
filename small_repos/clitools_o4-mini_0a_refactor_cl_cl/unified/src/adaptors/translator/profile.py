"""Adapter for translator.profile."""

from typing import Dict, Any, Optional
from ...utils.file_formats.json_util import json_safe_load, save_json_file

class ProfileManager:
    """Manager for user profiles."""
    
    def __init__(self, profile_path: str = 'profile.json'):
        """Initialize with path to profile file."""
        self.profile_path = profile_path
        self.profile = {}
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load profile from file."""
        self.profile = json_safe_load(self.profile_path, {})
        return self.profile
    
    def save(self) -> None:
        """Save profile to file."""
        save_json_file(self.profile, self.profile_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a profile value."""
        return self.profile.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a profile value."""
        self.profile[key] = value
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire profile."""
        return self.profile.copy()
    
    def clear(self) -> None:
        """Clear the profile."""
        self.profile = {}
        self.save()
