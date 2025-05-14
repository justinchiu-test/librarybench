"""
Secrets management module for CLI tools.
Securely manages credentials and sensitive configuration.
"""

import base64
import json
import os
import sys
import getpass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Try to import optional dependencies
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class StorageBackend(Enum):
    """Supported secret storage backends."""
    ENV = "env"           # Environment variables
    FILE = "file"         # Encrypted file
    KEYRING = "keyring"   # System keyring/keychain
    MEMORY = "memory"     # In-memory only (for testing)


class SecretManager:
    """
    Manages secrets for CLI applications.
    Provides secure storage and retrieval of sensitive information.
    """
    
    def __init__(self, 
                app_name: str,
                storage: Union[StorageBackend, str] = StorageBackend.ENV,
                secrets_file: Optional[str] = None,
                env_prefix: str = ""):
        """
        Initialize a new secret manager.
        
        Args:
            app_name: Name of the application
            storage: Storage backend to use
            secrets_file: Path to secrets file (for FILE backend)
            env_prefix: Prefix for environment variables (for ENV backend)
        """
        self.app_name = app_name
        
        # Normalize storage backend
        if isinstance(storage, str):
            try:
                self.storage = StorageBackend(storage.lower())
            except ValueError:
                self.storage = StorageBackend.ENV
        else:
            self.storage = storage
        
        self.env_prefix = env_prefix
        self.secrets_file = secrets_file
        
        # In-memory storage for MEMORY backend
        self._memory_storage: Dict[str, str] = {}
        
        # Check if selected backend is available
        if self.storage == StorageBackend.KEYRING and not KEYRING_AVAILABLE:
            print("Warning: Keyring backend not available. Falling back to ENV.")
            self.storage = StorageBackend.ENV
            
        if self.storage == StorageBackend.FILE and not CRYPTO_AVAILABLE:
            print("Warning: Cryptography library not available. Falling back to ENV.")
            self.storage = StorageBackend.ENV
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Store a secret.
        
        Args:
            key: Key to store the secret under
            value: Secret value to store
        """
        if self.storage == StorageBackend.ENV:
            env_key = f"{self.env_prefix}{key}".upper()
            os.environ[env_key] = value
            
        elif self.storage == StorageBackend.KEYRING:
            if not KEYRING_AVAILABLE:
                raise RuntimeError("Keyring not available")
            keyring.set_password(self.app_name, key, value)
            
        elif self.storage == StorageBackend.FILE:
            if not CRYPTO_AVAILABLE:
                raise RuntimeError("Cryptography library not available")
            self._save_to_file(key, value)
            
        elif self.storage == StorageBackend.MEMORY:
            self._memory_storage[key] = value
    
    def get_secret(self, key: str, prompt: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret.
        
        Args:
            key: Key to retrieve
            prompt: Prompt to show if secret not found and should be requested
            
        Returns:
            Secret value or None if not found
        """
        value = None
        
        if self.storage == StorageBackend.ENV:
            env_key = f"{self.env_prefix}{key}".upper()
            value = os.environ.get(env_key)
            
        elif self.storage == StorageBackend.KEYRING:
            if not KEYRING_AVAILABLE:
                raise RuntimeError("Keyring not available")
            value = keyring.get_password(self.app_name, key)
            
        elif self.storage == StorageBackend.FILE:
            if not CRYPTO_AVAILABLE:
                raise RuntimeError("Cryptography library not available")
            value = self._load_from_file(key)
            
        elif self.storage == StorageBackend.MEMORY:
            value = self._memory_storage.get(key)
        
        # If not found and prompt provided, request it
        if value is None and prompt:
            value = self._request_secret(prompt)
            if value:
                self.set_secret(key, value)
        
        return value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if not found
        """
        if self.storage == StorageBackend.ENV:
            env_key = f"{self.env_prefix}{key}".upper()
            if env_key in os.environ:
                del os.environ[env_key]
                return True
            return False
            
        elif self.storage == StorageBackend.KEYRING:
            if not KEYRING_AVAILABLE:
                raise RuntimeError("Keyring not available")
            try:
                keyring.delete_password(self.app_name, key)
                return True
            except keyring.errors.PasswordDeleteError:
                return False
            
        elif self.storage == StorageBackend.FILE:
            if not CRYPTO_AVAILABLE:
                raise RuntimeError("Cryptography library not available")
            return self._delete_from_file(key)
            
        elif self.storage == StorageBackend.MEMORY:
            if key in self._memory_storage:
                del self._memory_storage[key]
                return True
            return False
    
    def _request_secret(self, prompt: str) -> str:
        """Request a secret from the user via the console."""
        return getpass.getpass(prompt)
    
    def _get_secrets_file_path(self) -> Path:
        """Get the path to the secrets file."""
        if self.secrets_file:
            return Path(self.secrets_file)
        
        # Default location based on OS
        if sys.platform == 'win32':
            base_dir = Path(os.environ.get('APPDATA', '')) / self.app_name
        elif sys.platform == 'darwin':
            base_dir = Path.home() / 'Library' / 'Application Support' / self.app_name
        else:
            # Linux and others
            base_dir = Path.home() / '.config' / self.app_name
        
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / 'secrets.json'
    
    def _get_encryption_key(self) -> bytes:
        """
        Get or create the encryption key.
        Uses a password-based KDF to derive the key.
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        # Use a fixed salt for simplicity (not ideal for production)
        salt = b'clitools'
        
        # Get password
        password = os.environ.get('CLITOOLS_SECRET_KEY')
        if not password:
            password = getpass.getpass(
                f"Enter encryption password for {self.app_name}: ")
            
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _save_to_file(self, key: str, value: str) -> None:
        """Save a secret to the encrypted file."""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        file_path = self._get_secrets_file_path()
        
        # Load existing secrets
        secrets = {}
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    encrypted_data = f.read()
                
                # Decrypt
                encryption_key = self._get_encryption_key()
                fernet = Fernet(encryption_key)
                decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
                secrets = json.loads(decrypted_data)
            except Exception:
                # If any error occurs, start with empty secrets
                secrets = {}
        
        # Update with new secret
        secrets[key] = value
        
        # Encrypt and save
        encryption_key = self._get_encryption_key()
        fernet = Fernet(encryption_key)
        encrypted_data = fernet.encrypt(json.dumps(secrets).encode())
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
    
    def _load_from_file(self, key: str) -> Optional[str]:
        """Load a secret from the encrypted file."""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        file_path = self._get_secrets_file_path()
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            
            # Decrypt
            encryption_key = self._get_encryption_key()
            fernet = Fernet(encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
            secrets = json.loads(decrypted_data)
            
            return secrets.get(key)
        except Exception:
            return None
    
    def _delete_from_file(self, key: str) -> bool:
        """Delete a secret from the encrypted file."""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        file_path = self._get_secrets_file_path()
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r') as f:
                encrypted_data = f.read()
            
            # Decrypt
            encryption_key = self._get_encryption_key()
            fernet = Fernet(encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
            secrets = json.loads(decrypted_data)
            
            if key not in secrets:
                return False
            
            # Remove the key
            del secrets[key]
            
            # Encrypt and save
            encrypted_data = fernet.encrypt(json.dumps(secrets).encode())
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception:
            return False


# Create a global secret manager for convenience
_global_manager = SecretManager("clitools")

def set_secret(key: str, value: str) -> None:
    """Set a secret using the global manager."""
    _global_manager.set_secret(key, value)

def get_secret(key: str, prompt: Optional[str] = None) -> Optional[str]:
    """Get a secret using the global manager."""
    return _global_manager.get_secret(key, prompt)

def delete_secret(key: str) -> bool:
    """Delete a secret using the global manager."""
    return _global_manager.delete_secret(key)

def configure(app_name: str, **kwargs) -> None:
    """Configure the global secret manager."""
    global _global_manager
    _global_manager = SecretManager(app_name, **kwargs)