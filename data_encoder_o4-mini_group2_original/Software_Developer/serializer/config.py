"""
Global decoding configuration.
"""

# Default decoding settings
decoding_settings = {
    # When True, all lists in the decoded object graph are wrapped in LazyList
    "lazy": False,
}

def decoding_configuration(settings):
    """
    Update decoding settings. E.g. decoding_configuration({'lazy': True})
    """
    if not isinstance(settings, dict):
        raise ValueError("settings must be a dict")
    decoding_settings.update(settings)
