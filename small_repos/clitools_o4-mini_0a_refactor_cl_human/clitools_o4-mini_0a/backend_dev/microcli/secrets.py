def manage_secrets(provider: str, key: str) -> str:
    if not provider or not key:
        raise ValueError("Provider and key required")
    return f"{provider}:{key}:secret"
