# Shared utility functions for all modules
# IMPORTANT: This file must work when imported by different modules in different directories

def pad_list(lst, length, fill):
    """
    Pad or truncate list to specified length.
    """
    return (lst + [fill] * length)[:length]

def transform_dict(d, fn):
    """
    Apply fn to each value in dict and return a new dict.
    """
    return {k: fn(v) for k, v in d.items()}

def transform_list(lst, fn):
    """
    Apply fn to each element in list and return a new list.
    """
    return [fn(v) for v in lst]

def compress_str(s, threshold):
    """
    Compress string longer than threshold using zlib + base64.
    """
    if len(s) > threshold:
        import zlib, base64
        comp = zlib.compress(s.encode('utf-8'))
        b64 = base64.b64encode(comp).decode('ascii')
        return {'__compressed__': True, 'data': b64}
    return s

def decompress_entry(entry):
    """
    Decompress entry if it's a compressed marker, else return None.
    """
    if isinstance(entry, dict) and entry.get('__compressed__') and 'data' in entry:
        import zlib, base64
        comp = base64.b64decode(entry['data'])
        return zlib.decompress(comp).decode('utf-8')
    return None

def dict_to_xml(data, parent):
    """
    Recursively build XML elements from Python dict/list/primitive.
    """
    import xml.etree.ElementTree as ET
    if isinstance(data, dict):
        for key, value in data.items():
            elem = ET.SubElement(parent, key)
            dict_to_xml(value, elem)
    elif isinstance(data, list):
        for item in data:
            item_elem = ET.SubElement(parent, 'item')
            dict_to_xml(item, item_elem)
    else:
        parent.text = str(data)

def convert_text(text):
    """
    Attempt to convert text to int, float, bool, or leave as string.
    """
    if text is None:
        return None
    t = text.strip()
    if t.lower() in ('true', 'false'):
        return t.lower() == 'true'
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        pass
    return t

def xml_to_dict(elem):
    """
    Recursively convert an XML element (and children) back to Python data.
    """
    children = list(elem)
    if not children:
        return convert_text(elem.text)
    if all(child.tag == 'item' for child in children):
        return [xml_to_dict(child) for child in children]
    result = {}
    for child in children:
        result[child.tag] = xml_to_dict(child)
    return result
