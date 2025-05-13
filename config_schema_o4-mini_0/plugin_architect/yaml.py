"""
A minimal YAML stub for safe_dump and safe_load,
so that 'import yaml' in tests will find this module.
Supports only simple mappings and nested mappings,
booleans, ints, floats, and bare strings (no lists).
"""

def safe_dump(data):
    def _dump(item, indent=0):
        out = ''
        pad = ' ' * indent
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, dict):
                    out += f"{pad}{k}:\n"
                    out += _dump(v, indent+2)
                else:
                    # format scalar
                    if isinstance(v, bool):
                        val = 'true' if v else 'false'
                    else:
                        val = v
                    out += f"{pad}{k}: {val}\n"
        else:
            # fallback for non-dict
            out += f"{pad}{item}\n"
        return out

    return _dump(data).rstrip('\n') + '\n'


def safe_load(stream):
    """
    Load from a string or file-like of our very simple YAML.
    Only handles nested dicts via indentation (2 spaces per level)
    and scalars (int, float, bool, bare strings).
    """
    # get lines
    if isinstance(stream, str):
        lines = stream.splitlines()
    else:
        # file-like
        lines = stream.readlines()

    root = {}
    # stack of (expected_indent, current_dict)
    stack = [(0, root)]

    for raw in lines:
        line = raw.rstrip('\n')
        if not line or line.lstrip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip(' '))
        text = line.lstrip(' ')
        if ':' not in text:
            continue
        key, rest = text.split(':', 1)
        key = key.strip()
        val = rest.strip()

        # find correct parent based on indent
        while stack and indent < stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if val == '':
            # new nested mapping
            new_map = {}
            parent[key] = new_map
            # next expected children have indent = current indent + 2
            stack.append((indent+2, new_map))
        else:
            # parse scalar
            rawv = val
            low = rawv.lower()
            if low == 'true':
                value = True
            elif low == 'false':
                value = False
            else:
                # try int or float
                try:
                    if '.' in rawv:
                        value = float(rawv)
                    else:
                        value = int(rawv)
                except ValueError:
                    value = rawv
            parent[key] = value

    return root
