"""
Secrets management for operations engineer CLI tools.
"""

from typing import Dict, Optional, Any


class SecretManager:
    """Manager for handling secrets."""
    
    def __init__(self):
        """Initialize an empty secret manager."""
        self._secrets = {}
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Set a secret value.
        
        Args:
            key (str): Secret key.
            value (str): Secret value.
        """
        self._secrets[key] = value
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value.
        
        Args:
            key (str): Secret key.
            default (str, optional): Default value if key not found.
            
        Returns:
            str or None: Secret value or default.
        """
        return self._secrets.get(key, default)