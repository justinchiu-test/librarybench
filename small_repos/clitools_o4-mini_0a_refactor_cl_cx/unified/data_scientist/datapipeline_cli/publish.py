import re

def publish_package(repository_url=None):
    """
    Simulate publishing a package to a repository
    
    Args:
        repository_url: URL of the repository to publish to
            (defaults to PyPI)
    
    Returns:
        bool: True if publishing is successful
        
    Raises:
        ValueError: If repository URL is invalid
    """
    if repository_url is None:
        # Default to PyPI
        return True
    
    # Basic URL validation
    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(url_pattern, repository_url):
        raise ValueError(f"Invalid repository URL: {repository_url}")
    
    return True