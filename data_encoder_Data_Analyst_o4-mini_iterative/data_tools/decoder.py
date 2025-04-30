from .utils import type_from_name

def decode(encoded_data):
    """
    Decode data from the intermediate representation back to original form.
    Supports types encoded by encode().
    """
    if not isinstance(encoded_data, dict) or not encoded_data.get('__encoded__'):
        # Not encoded, return as-is
        return encoded_data
    t = encoded_data.get('type')
    if t == 'primitive':
        return encoded_data['value']
    if t == 'homogeneous_primitive_list':
        elem_type = type_from_name(encoded_data['elem_type'])
        return [elem_type(e) for e in encoded_data['data']]
    if t == 'homogeneous_dict_list':
        schema = encoded_data['schema']
        keys = encoded_data['keys']
        data = encoded_data['data']
        result = []
        for row in data:
            d = {}
            for k, v in zip(keys, row):
                tp = type_from_name(schema[k])
                d[k] = tp(v)
            result.append(d)
        return result
    if t == 'list':
        types = encoded_data['types']
        data = encoded_data['data']
        result = []
        for tp_name, v in zip(types, data):
            tp = type_from_name(tp_name)
            result.append(tp(v))
        return result
    if t == 'dict':
        keys = encoded_data['keys']
        types = encoded_data['types']
        values = encoded_data['values']
        d = {}
        for k, tp_name, v in zip(keys, types, values):
            tp = type_from_name(tp_name)
            d[k] = tp(v)
        return d
    raise ValueError(f"Unsupported encoded data type: {t}")
