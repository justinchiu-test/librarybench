"""
Adapter for backend_dev.microcli.publish.
"""

import re
from typing import Optional

def publish_package(repo_url: Optional[str] = None) -> bool:
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