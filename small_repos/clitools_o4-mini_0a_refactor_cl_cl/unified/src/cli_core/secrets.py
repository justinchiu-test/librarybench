"""
Secrets management for CLI applications.

This module provides utilities for securely handling sensitive information.
"""

import os
import json
import base64
import re
from typing import Dict, Any, Optional, Union, List


class SecretsManager:
    """
    Manages sensitive configuration values.
    
    Provides secure access to secrets through environment variables or files.
    """
    
    def __init__(self, prefix: str = "", 
                secrets_file: Optional[str] = None, 
                default_values: Dict[str, str] = None):
        """
        Initialize the secrets manager.
        
        Args:
            prefix (str): Prefix for environment variables.
            secrets_file (str, optional): Path to a secrets file.
            default_values (Dict[str, str], optional): Default values for secrets.
        """
        self.prefix = prefix
        self.secrets_file = secrets_file
        self.default_values = default_values or {}
        self._loaded_secrets = {}
        
        # Load secrets from file if provided
        if secrets_file and os.path.exists(secrets_file):
            self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Load secrets from the secrets file."""
        try:
            with open(self.secrets_file, 'r') as f:
                content = f.read().strip()
                
                # Check if content is JSON
                if content.startswith('{') and content.endswith('}'):
                    self._loaded_secrets = json.loads(content)
                else:
                    # Treat as key=value pairs
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self._loaded_secrets[key.strip()] = value.strip()
        except (IOError, json.JSONDecodeError, ValueError):
            self._loaded_secrets = {}
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value.
        
        The order of precedence is:
        1. Environment variable with prefix
        2. Environment variable without prefix
        3. Value from secrets file
        4. Default value provided during initialization
        5. Default value provided to this method
        
        Args:
            key (str): Secret key.
            default (str, optional): Default value if secret not found.
            
        Returns:
            str or None: Secret value or None if not found.
        """
        # Check environment variables with prefix
        if self.prefix:
            env_key = f"{self.prefix}{key}"
            if env_key in os.environ:
                return os.environ[env_key]
        
        # Check environment variables without prefix
        if key in os.environ:
            return os.environ[key]
        
        # Check loaded secrets
        if key in self._loaded_secrets:
            return self._loaded_secrets[key]
        
        # Check default values
        if key in self.default_values:
            return self.default_values[key]
        
        # Return provided default
        return default
    
    def validate(self, required_keys: List[str]) -> List[str]:
        """
        Validate that all required keys are available.
        
        Args:
            required_keys (List[str]): List of required secret keys.
            
        Returns:
            List[str]: List of missing keys.
        """
        missing = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing.append(key)
        
        return missing
    
    def export_to_env(self) -> None:
        """Export all secrets to environment variables."""
        # Export from default values
        for key, value in self.default_values.items():
            if key not in os.environ:
                os.environ[key] = value
        
        # Export from loaded secrets (overrides defaults)
        for key, value in self._loaded_secrets.items():
            if key not in os.environ:
                os.environ[key] = value


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret from the environment.
    
    Args:
        key (str): Secret key.
        default (str, optional): Default value if secret not found.
        
    Returns:
        str or None: Secret value or None if not found.
    """
    return os.environ.get(key, default)


def validate_secrets(required_keys: List[str]) -> List[str]:
    """
    Validate that required secrets are set in the environment.
    
    Args:
        required_keys (List[str]): List of required secret keys.
        
    Returns:
        List[str]: List of missing secret keys.
    """
    missing = []
    
    for key in required_keys:
        if key not in os.environ:
            missing.append(key)
    
    return missing