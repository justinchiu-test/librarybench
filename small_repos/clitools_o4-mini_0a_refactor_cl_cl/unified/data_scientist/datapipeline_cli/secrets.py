"""
Secrets management for data scientist CLI tools.
"""

import os
from typing import Dict, List, Any


def manage_secrets(keys: List[str], store_type: str = None) -> Dict[str, str]:
    """
    Manage and retrieve secrets for the given keys.
    
    Args:
        keys (List[str]): List of secret keys to retrieve.
        store_type (str, optional): Type of secret store to use.
                                   If not provided, uses value from SECRET_STORE env var.
    
    Returns:
        Dict[str, str]: Dictionary of secret keys and values.
        
    Raises:
        KeyError: If a secret key is not found.
    """
    # Determine store type from environment if not provided
    if store_type is None:
        store_type = os.environ.get('SECRET_STORE', 'env')
    
    # Initialize result
    secrets = {}
    
    # Get secrets based on store type
    if store_type == 'env':
        # Get secrets from environment variables
        for key in keys:
            if key in os.environ:
                secrets[key] = os.environ[key]
            else:
                raise KeyError(f"Secret not found: {key}")
    else:
        raise ValueError(f"Unsupported secret store type: {store_type}")
    
    return secrets