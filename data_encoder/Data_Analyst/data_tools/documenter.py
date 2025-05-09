import inspect
from .encoder import encode
from .decoder import decode
from .validator import validate

def document_api():
    """
    Generate documentation for the API functions.
    Returns a string containing function signatures and docstrings.
    """
    docs = []
    funcs = [encode, decode, validate, document_api]
    for fn in funcs:
        sig = str(inspect.signature(fn))
        doc = inspect.getdoc(fn) or ''
        docs.append(f"{fn.__name__}{sig}\n{doc}")
    return "\n\n".join(docs)
