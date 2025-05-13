"""
Package publishing for backend_dev microcli.
Validates repository URL or uses default.
"""
from urllib.parse import urlparse

def publish_package(repo_url=None):
    """
    Publish a package. Returns True on success; raises ValueError on invalid URL.
    """
    if repo_url is None:
        return True
    parsed = urlparse(repo_url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL: {repo_url}")
    return True