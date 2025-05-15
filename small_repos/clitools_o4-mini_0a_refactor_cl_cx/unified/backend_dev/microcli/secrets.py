import os
import base64

def manage_secrets(service, key):
    """
    Manage secrets for services
    
    Args:
        service: Service name
        key: Secret key
        
    Returns:
        str: An identifier for the secret
        
    Raises:
        ValueError: If service or key is empty
    """
    if not service or not key:
        raise ValueError("Service and key must not be empty")
    
    # Create a unique identifier for this secret
    identifier = f"{service}:{key}"
    
    # In a real implementation, this would securely store the secret
    # For demo purposes, we're just returning the identifier
    
    return identifier