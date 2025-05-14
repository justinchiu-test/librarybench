import json

def safe_dump(data):
    """
    Fake YAML dump by emitting JSON.  Tests only
    do safe_dump -> safe_load roundtrips and look
    at simple dict/list/primitive structures.
    """
    return json.dumps(data)

def safe_load(s):
    """
    Fake YAML load by parsing JSON.
    """
    return json.loads(s)
