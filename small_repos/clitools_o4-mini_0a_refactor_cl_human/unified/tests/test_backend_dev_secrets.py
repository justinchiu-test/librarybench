import pytest
from src.core.infra.secrets import SecretManager, StorageBackend

def test_set_get_secret():
    # Create a secret manager
    manager = SecretManager("test-app", storage=StorageBackend.MEMORY)
    
    # Set a secret
    manager.set_secret("api_key", "secret-value")
    
    # Get the secret
    value = manager.get_secret("api_key")
    
    # Verify
    assert value == "secret-value"

def test_missing_secret():
    # Create a secret manager
    manager = SecretManager("test-app", storage=StorageBackend.MEMORY)
    
    # Try to get a non-existent secret
    value = manager.get_secret("non_existent")
    
    # Verify it returns None
    assert value is None

def test_delete_secret():
    # Create a secret manager
    manager = SecretManager("test-app", storage=StorageBackend.MEMORY)
    
    # Set a secret
    manager.set_secret("temp_key", "temp-value")
    
    # Verify it exists
    assert manager.get_secret("temp_key") == "temp-value"
    
    # Delete the secret
    deleted = manager.delete_secret("temp_key")
    
    # Verify it was deleted
    assert deleted
    assert manager.get_secret("temp_key") is None