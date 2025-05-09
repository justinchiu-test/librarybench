from registry import Registry

def search_packages(registry, name=None, version=None):
    """
    Returns list of dicts with package metadata that match the search.
    """
    pkgs = registry.search(name_substr=name, version_spec=version)
    return [p.to_dict() for p in pkgs]
