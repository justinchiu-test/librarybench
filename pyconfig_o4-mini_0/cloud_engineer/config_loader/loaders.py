# custom_format_loaders

import xml.etree.ElementTree as ET
import re

def load_toml(path: str) -> dict:
    """
    Load a simple TOML-like file and return as dict.
    Supports flat key = value pairs, where value can be:
      - integer (e.g., 42)
      - float (e.g., 3.14)
      - quoted string (e.g., "hello")
      - boolean true/false
    """
    result = {}
    with open(path, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            # Skip empty lines or comments
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = map(str.strip, line.split('=', 1))
            # String
            if val.startswith('"') and val.endswith('"'):
                result[key] = val[1:-1]
            # Boolean
            elif val.lower() in ('true', 'false'):
                result[key] = val.lower() == 'true'
            else:
                # Float
                if re.match(r'^-?\d+\.\d+$', val):
                    try:
                        result[key] = float(val)
                        continue
                    except ValueError:
                        pass
                # Integer
                if re.match(r'^-?\d+$', val):
                    try:
                        result[key] = int(val)
                        continue
                    except ValueError:
                        pass
                # Fallback to raw string
                result[key] = val
    return result

def _etree_to_dict(elem):
    d = {}
    for child in elem:
        if len(child):
            d[child.tag] = _etree_to_dict(child)
        else:
            d[child.tag] = child.text
    return d

def load_xml(path: str) -> dict:
    """
    Load an XML file and return as dict.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    return {root.tag: _etree_to_dict(root)}
