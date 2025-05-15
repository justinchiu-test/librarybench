"""
Secrets management module for the Translator persona.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class SecretsManager:
    """
    Manages access to secrets from various sources.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the secrets manager.
        
        Args:
            config_dir: Directory containing configuration and secrets
        """
        self.config_dir = config_dir or Path.home() / '.translator'
        self.secrets_file = self.config_dir / 'secrets.json'
        self._secrets_cache: Dict[str, Any] = {}
        self._loaded = False
    
    def _ensure_loaded(self) -> None:
        """Ensure secrets are loaded from storage."""
        if self._loaded:
            return
        
        self._load_from_file()
        self._load_from_env()
        self._loaded = True
    
    def _load_from_file(self) -> None:
        """Load secrets from the secrets file."""
        if not self.secrets_file.exists():
            return
        
        try:
            with self.secrets_file.open('r') as f:
                self._secrets_cache.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            # Silently fail on errors, secrets will be unavailable
            pass
    
    def _load_from_env(self) -> None:
        """Load secrets from environment variables."""
        # Look for environment variables prefixed with TRANSLATOR_SECRET_
        prefix = 'TRANSLATOR_SECRET_'
        for key, value in os.environ.items():
            if key.startswith(prefix):
                secret_name = key[len(prefix):].lower()
                self._secrets_cache[secret_name] = value
    
    def get_secret(self, name: str, default: Any = None) -> Any:
        """
        Get a secret by name.
        
        Args:
            name: Secret identifier
            default: Default value if secret is not found
            
        Returns:
            The secret value or default if not found
        """
        self._ensure_loaded()
        return self._secrets_cache.get(name, default)
    
    def set_secret(self, name: str, value: Any) -> None:
        """
        Set a secret value.
        
        Args:
            name: Secret identifier
            value: Secret value
        """
        self._ensure_loaded()
        self._secrets_cache[name] = value
    
    def save_secrets(self) -> bool:
        """
        Save secrets to the secrets file.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with self.secrets_file.open('w') as f:
                json.dump(self._secrets_cache, f, indent=2)
            return True
        except OSError:
            return False


# Global secrets manager instance
_secrets_manager = SecretsManager()


def get_secret(name: str, default: Any = None) -> Any:
    """
    Get a secret by name.
    
    Args:
        name: Secret identifier
        default: Default value if secret is not found
        
    Returns:
        The secret value or default if not found
    """
    return _secrets_manager.get_secret(name, default)


def set_secret(name: str, value: Any) -> None:
    """
    Set a secret value.
    
    Args:
        name: Secret identifier
        value: Secret value
    """
    _secrets_manager.set_secret(name, value)


def save_secrets() -> bool:
    """
    Save secrets to storage.
    
    Returns:
        True if save was successful, False otherwise
    """
    return _secrets_manager.save_secrets()