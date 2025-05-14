class SymlinkConfig:
    """Configuration for symlink handling."""
    def __init__(self, follow_links: bool = False):
        self.follow_links = follow_links
