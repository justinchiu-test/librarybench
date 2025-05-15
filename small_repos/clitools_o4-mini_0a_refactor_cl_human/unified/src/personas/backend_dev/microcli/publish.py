import re

def publish_package(repository_url: str = "https://pypi.org/") -> bool:
    """
    Simulates publishing a package to a repository.
    
    Args:
        repository_url: URL of the repository to publish to
        
    Returns:
        True if the publish operation would succeed
        
    Raises:
        ValueError: If the repository URL is invalid
    """
    # Very basic URL validation
    if not re.match(r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*', repository_url):
        raise ValueError(f"Invalid repository URL: {repository_url}")
        
    # In a real implementation, this would actually publish the package
    # For now, just return True to indicate success
    return True