def next_version(existing_versions):
    """
    Determine the next version number given a list of existing versions.
    """
    return max(existing_versions) + 1 if existing_versions else 1
