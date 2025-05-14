"""Adapter for backend_dev.microcli.secrets."""

from typing import List

from ....cli_core.secrets import validate_secrets

# Re-export the function for backward compatibility

def manage_secrets(provider: str, secret_name: str) -> str:
    """
    Manage secrets for a provider.

    Args:
        provider: Provider name.
        secret_name: Secret name.

    Returns:
        str: Secret reference.

    Raises:
        ValueError: If provider or secret_name is empty.
    """
    if not provider or not secret_name:
        raise ValueError("Provider and secret name must not be empty")

    # This is a mock implementation for testing
    return f"{provider}:{secret_name}:{hash(provider + secret_name) % 1000:03d}"
