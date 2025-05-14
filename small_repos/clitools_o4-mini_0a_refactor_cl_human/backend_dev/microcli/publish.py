def publish_package(index_url: str = "https://pypi.org") -> bool:
    # Stub implementation: in real world would run twine
    if not index_url.startswith("http"):
        raise ValueError("Invalid index URL")
    return True
