import json

def safe_dump(data, stream=None):
    """
    Dump Python data structures to the given stream (or return a string),
    using JSON formatting (a subset of YAML).
    """
    text = json.dumps(data)
    if stream:
        stream.write(text)
    else:
        return text

def safe_load(stream_or_str):
    """
    Load data from a stream or string, interpreting it as JSON.
    Returns the parsed Python data structure, or {} on empty/invalid input.
    """
    if hasattr(stream_or_str, 'read'):
        content = stream_or_str.read()
    else:
        content = stream_or_str or ''
    content = content.strip()
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback empty mapping
        return {}
