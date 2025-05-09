from .utils import type_name

def encode(data, config=None):
    """
    Encode the given data structure into an intermediate representation.
    Supports:
    - Homogeneous primitive lists
    - Homogeneous dict lists
    - Generic lists
    - Generic dicts
    - Primitive values
    """
    # Primitive types
    if isinstance(data, (int, float, str, bool)):
        return {
            '__encoded__': True,
            'type': 'primitive',
            'value': data,
            'value_type': type_name(type(data))
        }
    # Lists, tuples, sets
    if isinstance(data, (list, tuple, set)):
        data_list = list(data)
        if not data_list:
            # Empty list
            return {
                '__encoded__': True,
                'type': 'list',
                'data': [],
                'types': []
            }
        # Determine element type names
        elem_type_names = [type_name(type(e)) for e in data_list]
        unique_elem_types = set(elem_type_names)
        if len(unique_elem_types) == 1:
            elem_type = elem_type_names[0]
            if elem_type in ('int', 'float', 'str', 'bool'):
                return {
                    '__encoded__': True,
                    'type': 'homogeneous_primitive_list',
                    'elem_type': elem_type,
                    'data': data_list
                }
            if elem_type == 'dict':
                # Homogeneous dict list
                keys = sorted(data_list[0].keys())
                schema = {k: type_name(type(data_list[0][k])) for k in keys}
                for d in data_list[1:]:
                    if set(d.keys()) != set(keys):
                        raise ValueError("Inconsistent dict keys in homogeneous dict list")
                    for k in keys:
                        if type_name(type(d[k])) != schema[k]:
                            raise ValueError("Inconsistent dict value types in homogeneous dict list")
                values = [[d[k] for k in keys] for d in data_list]
                return {
                    '__encoded__': True,
                    'type': 'homogeneous_dict_list',
                    'schema': schema,
                    'keys': keys,
                    'data': values
                }
        # Generic list
        return {
            '__encoded__': True,
            'type': 'list',
            'data': data_list,
            'types': elem_type_names
        }
    # Dict
    if isinstance(data, dict):
        keys = list(data.keys())
        values = [data[k] for k in keys]
        types = [type_name(type(v)) for v in values]
        return {
            '__encoded__': True,
            'type': 'dict',
            'keys': keys,
            'types': types,
            'values': values
        }
    # Unsupported type
    raise ValueError(f"Unsupported data type: {type(data)}")
