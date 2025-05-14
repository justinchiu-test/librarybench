"""
Package publishing utilities for backend developer CLI tools.
"""

import re

def publish_package(repo_url=None):
    """
    Publish a package to a repository.
    
    Args:
        repo_url (str, optional): Repository URL.
        
    Returns:
        bool: Always True for default implementation.
        
    Raises:
        ValueError: If URL is invalid.
    """
    # Default success for mock implementation
    if repo_url is None:
        return True
    
    # Validate URL format if provided
    url_pattern = r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}.*$'
    if not re.match(url_pattern, repo_url):
        raise ValueError(f"Invalid repository URL: {repo_url}")
    
    return True