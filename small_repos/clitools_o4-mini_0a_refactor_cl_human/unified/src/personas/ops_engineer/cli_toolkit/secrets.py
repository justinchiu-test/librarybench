"""
Secrets management for the CLI Toolkit.
"""
import os
import json
from typing import Any, Dict, List, Optional, Union


class SecretManager:
    """
    Manages secrets for the CLI toolkit.
    """
    
    def __init__(self, secret_file: Optional[str] = None):
        """
        Initialize a new secret manager.
        
        Args:
            secret_file: Path to secrets file
        """
        self.secret_file = secret_file or os.path.expanduser("~/.cli_toolkit/secrets.json")
        self.secrets = {}
        self._load_secrets()
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Get a secret by key.
        
        Args:
            key: Secret key
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        # Check if key exists in environment variables
        env_key = f"CLI_TOOLKIT_SECRET_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # Return from secrets dict
        return self.secrets.get(key, default)
    
    def set_secret(self, key: str, value: Any) -> None:
        """
        Set a secret.
        
        Args:
            key: Secret key
            value: Secret value
        """
        self.secrets[key] = value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Secret key
            
        Returns:
            True if secret was deleted
        """
        if key in self.secrets:
            del self.secrets[key]
            return True
        return False
    
    def list_secrets(self) -> List[str]:
        """
        List all secret keys.
        
        Returns:
            List of secret keys
        """
        return list(self.secrets.keys())
    
    def _load_secrets(self) -> None:
        """Load secrets from file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.secret_file), exist_ok=True)
            
            # Load secrets if file exists
            if os.path.exists(self.secret_file):
                with open(self.secret_file, 'r') as f:
                    self.secrets = json.load(f)
        except Exception:
            # If any error occurs, start with empty secrets
            self.secrets = {}
    
    def save_secrets(self) -> bool:
        """
        Save secrets to file.
        
        Returns:
            True if successful
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.secret_file), exist_ok=True)
            
            # Save secrets
            with open(self.secret_file, 'w') as f:
                json.dump(self.secrets, f)
            
            return True
        except Exception:
            return False