"""
Package publishing for backend developers.
"""
def publish_package(repo_url=None):
    """
    Dummy publish implementation for backend developers.
    If repo_url is None or a valid HTTP URL, return True; else raise ValueError.
    """
    if repo_url is None:
        return True
    if isinstance(repo_url, str) and repo_url.startswith(('http://', 'https://')):
        return True
    raise ValueError(f"Invalid repository URL: {repo_url}")