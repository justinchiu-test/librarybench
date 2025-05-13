# secret_manager_integration
def fetch_secret(manager: str, key: str) -> str:
    """
    Fetch a secret from the specified manager.
    Supported managers: 'aws', 'vault'
    """
    if manager == 'aws':
        return f"aws_secret_{key}"
    elif manager == 'vault':
        return f"vault_secret_{key}"
    else:
        raise ValueError(f"Unknown secret manager '{manager}'")

def rotate_secret(manager: str, key: str) -> str:
    """
    Rotate a secret in the specified manager.
    Returns the new secret value.
    """
    if manager == 'aws':
        return f"aws_rotated_{key}"
    elif manager == 'vault':
        return f"vault_rotated_{key}"
    else:
        raise ValueError(f"Unknown secret manager '{manager}'")
