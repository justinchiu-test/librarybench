"""
Secrets management for Data Pipeline CLI.
"""
import os
import json
import base64
from typing import Any, Dict, Optional
from pathlib import Path

class SecretsManager:
    """
    Manages secrets for data pipelines.
    """
    
    def __init__(self, secrets_file: Optional[str] = None):
        """
        Initialize a new secrets manager.
        
        Args:
            secrets_file: Path to secrets file
        """
        # Default secrets file location
        if secrets_file is None:
            self.secrets_file = str(Path.home() / ".datapipeline" / "secrets.json")
        else:
            self.secrets_file = secrets_file
        
        self.secrets: Dict[str, Any] = {}
        self._loaded = False
    
    def load(self) -> bool:
        """
        Load secrets from file.
        
        Returns:
            True if secrets were loaded successfully
        """
        # Don't reload if already loaded
        if self._loaded:
            return True
        
        # Try to load from file
        if os.path.exists(self.secrets_file):
            try:
                with open(self.secrets_file, 'r') as f:
                    self.secrets = json.load(f)
                self._loaded = True
                return True
            except (IOError, json.JSONDecodeError):
                return False
        
        # File doesn't exist, but that's okay
        self._loaded = True
        return True
    
    def save(self) -> bool:
        """
        Save secrets to file.
        
        Returns:
            True if secrets were saved successfully
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.secrets_file), exist_ok=True)
            
            # Save secrets
            with open(self.secrets_file, 'w') as f:
                json.dump(self.secrets, f)
                
            return True
        except IOError:
            return False
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Get a secret by key.
        
        Args:
            key: Secret key
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # Load secrets if not already loaded
        if not self._loaded:
            self.load()
        
        # Try to get secret from environment
        env_key = f"DATAPIPELINE_SECRET_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # Get from secrets dictionary
        return self.secrets.get(key, default)
    
    def set_secret(self, key: str, value: Any) -> None:
        """
        Set a secret.
        
        Args:
            key: Secret key
            value: Secret value
        """
        # Load secrets if not already loaded
        if not self._loaded:
            self.load()
        
        # Set secret
        self.secrets[key] = value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret key
            
        Returns:
            True if secret was deleted
        """
        # Load secrets if not already loaded
        if not self._loaded:
            self.load()
        
        # Delete secret if it exists
        if key in self.secrets:
            del self.secrets[key]
            return True
        
        return False
    
    def list_secrets(self) -> list:
        """
        List all secret keys.
        
        Returns:
            List of secret keys
        """
        # Load secrets if not already loaded
        if not self._loaded:
            self.load()
        
        return list(self.secrets.keys())
    
    def encrypt_value(self, value: str) -> str:
        """
        Basic encryption for a value (not secure, just an example).
        
        Args:
            value: Value to encrypt
            
        Returns:
            Encrypted value
        """
        # This is NOT secure encryption, just base64 encoding for demonstration
        # In a real application, use a proper encryption library
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Basic decryption for a value (not secure, just an example).
        
        Args:
            encrypted_value: Encrypted value
            
        Returns:
            Decrypted value
        """
        # This is NOT secure encryption, just base64 decoding for demonstration
        # In a real application, use a proper encryption library
        return base64.b64decode(encrypted_value.encode('utf-8')).decode('utf-8')

# Global secrets manager
_secrets_manager = SecretsManager()

def get_secret(key: str, default: Any = None) -> Any:
    """
    Get a secret from the global secrets manager.
    
    Args:
        key: Secret key
        default: Default value if secret not found
        
    Returns:
        Secret value or default
    """
    return _secrets_manager.get_secret(key, default)

def set_secret(key: str, value: Any) -> None:
    """
    Set a secret in the global secrets manager.
    
    Args:
        key: Secret key
        value: Secret value
    """
    _secrets_manager.set_secret(key, value)

def save_secrets() -> bool:
    """
    Save secrets in the global secrets manager.
    
    Returns:
        True if secrets were saved successfully
    """
    return _secrets_manager.save()

def list_secrets() -> list:
    """
    List all secret keys in the global secrets manager.
    
    Returns:
        List of secret keys
    """
    return _secrets_manager.list_secrets()


def manage_secrets(keys: list) -> Dict[str, str]:
    """
    Manage secrets from various sources.
    
    Args:
        keys: List of secret keys to retrieve
        
    Returns:
        Dictionary of secret keys and values
        
    Raises:
        KeyError: If a secret is not found
    """
    secrets = {}
    
    # Determine the secret store to use
    store = os.environ.get('SECRET_STORE', 'file').lower()
    
    if store == 'env':
        # Get secrets from environment variables
        for key in keys:
            if key in os.environ:
                secrets[key] = os.environ[key]
            else:
                raise KeyError(f"Secret not found: {key}")
    
    elif store == 'file':
        # Get secrets from file
        for key in keys:
            value = get_secret(key)
            if value is None:
                raise KeyError(f"Secret not found: {key}")
            secrets[key] = value
    
    else:
        raise ValueError(f"Unknown secret store: {store}")
    
    return secrets