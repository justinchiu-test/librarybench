"""
Registry for custom type encoders/decoders.
"""

_registry = {}  # maps class -> (encoder_fn, decoder_fn)

def custom_type_support(cls, encoder_fn, decoder_fn):
    """
    Register support for a custom type.
    encoder_fn(obj) -> a JSON-serializable structure (dict, list, etc.)
    decoder_fn(struct) -> obj
    """
    if not callable(encoder_fn) or not callable(decoder_fn):
        raise ValueError("encoder_fn and decoder_fn must be callable")
    _registry[cls] = (encoder_fn, decoder_fn)

def get_encoder(obj):
    """
    Find a registered encoder for this object (by type).
    Returns encoder_fn or None.
    """
    for cls, (enc, _) in _registry.items():
        if isinstance(obj, cls):
            return enc
    return None

def get_decoder(type_name):
    """
    Find a registered decoder by class name.
    Returns decoder_fn or None.
    """
    for cls, (_, dec) in _registry.items():
        if cls.__name__ == type_name:
            return dec
    return None
