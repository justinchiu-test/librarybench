PRIMITIVE_TYPES = {int, float, str, bool}

def type_name(t):
    if t in PRIMITIVE_TYPES:
        return t.__name__
    if t is dict:
        return 'dict'
    if t is list:
        return 'list'
    if t is tuple:
        return 'tuple'
    if t is set:
        return 'set'
    raise ValueError(f"Unsupported type: {t}")

def type_from_name(name):
    if name == 'int':
        return int
    if name == 'float':
        return float
    if name == 'str':
        return str
    if name == 'bool':
        return bool
    if name == 'dict':
        return dict
    if name == 'list':
        return list
    if name == 'tuple':
        return tuple
    if name == 'set':
        return set
    raise ValueError(f"Unsupported type name: {name}")
