"""
Core encoding/decoding routines.
"""
import json
from .registry import custom_type_support as register_custom, get_encoder, get_decoder
from .config import decoding_settings
from .lazy import LazyList

# ----- Public API functions ----- #

def custom_type_support(custom_type, encoder_fn, decoder_fn):
    """
    Register support for a custom type.
    """
    return register_custom(custom_type, encoder_fn, decoder_fn)

def encoding(data, format="json"):
    """
    Encode Python data into the given format.
    Currently only 'json' is supported.
    """
    if format != "json":
        raise ValueError(f"Unsupported format: {format}")

    class _CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            enc = get_encoder(obj)
            if enc:
                # Wrap it in a dict with a type marker
                return {"__type__": type(obj).__name__, "data": enc(obj)}
            # Let base class raise the default error
            return super().default(obj)

    return json.dumps(data, cls=_CustomJSONEncoder)

def decoding(serialized_str, format="json"):
    """
    Decode serialized string in the given format.
    """
    if format != "json":
        raise ValueError(f"Unsupported format: {format}")

    def _object_hook(d):
        # Handle custom types
        if "__type__" in d and "data" in d:
            type_name = d["__type__"]
            dec = get_decoder(type_name)
            if dec:
                return dec(d["data"])
        return d

    parsed = json.loads(serialized_str, object_hook=_object_hook)

    if decoding_settings.get("lazy", False):
        # Recursively wrap all lists in LazyList
        def _wrap(obj):
            if isinstance(obj, list):
                return LazyList([_wrap(item) for item in obj])
            elif isinstance(obj, dict):
                return {k: _wrap(v) for k, v in obj.items()}
            else:
                return obj
        return _wrap(parsed)
    else:
        return parsed

def cross_language_support(data, format="json"):
    """
    Alias for encoding with explicit format name.
    """
    return encoding(data, format=format)
