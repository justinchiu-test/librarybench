"""Secrets management for backend developer CLI tools."""

from src.cli_core.secrets import validate_secrets

def manage_secrets(provider, secret_name):
    """
    Manage secrets for a provider.

    Args:
        provider (str): Provider name.
        secret_name (str): Secret name.

    Returns:
        str: Secret reference.

    Raises:
        ValueError: If provider or secret_name is empty.
    """
    if not provider or not secret_name:
        raise ValueError("Provider and secret name must not be empty")

    # This is a mock implementation for testing
    return f"{provider}:{secret_name}:{hash(provider + secret_name) % 1000:03d}"