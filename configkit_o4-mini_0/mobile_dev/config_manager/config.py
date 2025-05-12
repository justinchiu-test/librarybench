import re
from .coercers import CoercerRegistry

class Config:
    def __init__(self):
        self._data = {}
        self.conflicts = []
        self.coercers = CoercerRegistry()

    def load_yaml(self, yaml_str):
        data = self._parse_yaml(yaml_str)
        self._data = self._merge_dicts(self._data, data, path=[])
        return self

    def load_yaml_file(self, path):
        with open(path, 'r') as f:
            return self.load_yaml(f.read())

    def merge(self, other_config):
        if isinstance(other_config, Config):
            data = other_config._data
        else:
            data = other_config
        self._data = self._merge_dicts(self._data, data, path=[])
        return self

    def _merge_dicts(self, base, override, path):
        result = dict(base)
        for key, val in override.items():
            if key in base:
                base_val = base[key]
                # nested dicts
                if isinstance(base_val, dict) and isinstance(val, dict):
                    result[key] = self._merge_dicts(base_val, val, path + [key])
                # list fallbacks
                elif isinstance(base_val, list) and isinstance(val, list) and (key.endswith('_fallback') or key == 'languages'):
                    merged = base_val + [item for item in val if item not in base_val]
                    result[key] = merged
                else:
                    if base_val != val:
                        self.conflicts.append(".".join(path + [key]))
                    result[key] = val
            else:
                result[key] = val
        return result

    def get(self, path, default=None):
        parts = path.split('.')
        node = self._data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        if isinstance(node, str):
            return self._interpolate(node)
        return node

    def set(self, path, value):
        parts = path.split('.')
        node = self._data
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = value

    def _interpolate(self, value):
        # match only non-nested placeholders first (no braces inside)
        pattern = re.compile(r'\$\{([^{}]+)\}')
        def repl(match):
            key = match.group(1)
            val = self.get(key, match.group(0))
            if isinstance(val, bool):
                return 'true' if val else 'false'
            return str(val)
        prev, curr = None, value
        while prev != curr:
            prev, curr = curr, pattern.sub(repl, curr)
        return curr

    def visualize(self):
        from .visualization import ConfigVisualization
        viz = ConfigVisualization(self._data)
        return viz.render()

    def register_coercer(self, name, func):
        self.coercers.register(name, func)

    def coerce(self, name, value):
        return self.coercers.coerce(name, value)

    def _parse_yaml(self, text):
        """
        A minimal YAML parser supporting:
        - nested mappings via indentation
        - lists via "- " entries
        - scalar types: ints, booleans, quoted strings, and plain strings
        """
        def parse_scalar(s):
            s_lower = s.lower()
            # null
            if s_lower in ('null', '~'):
                return None
            # booleans
            if s_lower == 'true':
                return True
            if s_lower == 'false':
                return False
            # quoted strings
            if (len(s) >= 2) and ((s[0] == s[-1] == "'") or (s[0] == s[-1] == '"')):
                return s[1:-1]
            # integers
            if re.fullmatch(r'-?\d+', s):
                try:
                    return int(s)
                except:
                    pass
            # fallback to string
            return s

        root = {}
        stack = [(-1, root)]
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith('#'):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(' '))
            line = raw_line.lstrip(' ')
            # List item
            if line.startswith('- '):
                val_str = line[2:].strip()
                val = parse_scalar(val_str)
                # find parent for this indent
                while stack and stack[-1][0] >= indent:
                    stack.pop()
                parent_indent, parent = stack[-1]
                if isinstance(parent, list):
                    parent.append(val)
                elif isinstance(parent, dict):
                    # convert placeholder dict into list if empty
                    if not parent:
                        # get grandparent
                        if len(stack) < 2:
                            continue
                        gp_indent, gp = stack[-2]
                        # find the key corresponding to this empty dict
                        for k, v in list(gp.items()):
                            if v is parent:
                                lst = []
                                gp[k] = lst
                                parent = lst
                                # update stack reference
                                stack[-1] = (parent_indent, parent)
                                break
                        else:
                            continue
                        parent.append(val)
                    else:
                        # convert last key into list if needed
                        last_key = list(parent.keys())[-1]
                        current = parent[last_key]
                        if not isinstance(current, list):
                            lst = []
                            parent[last_key] = lst
                            current = lst
                        current.append(val)
                # else unsupported parent type: skip
                continue

            # Mapping entry
            if ':' not in line:
                continue
            key_part, rest = line.split(':', 1)
            key = key_part.strip()
            val_str = rest.strip()
            # find correct parent for this indent
            while stack and stack[-1][0] >= indent:
                stack.pop()
            parent = stack[-1][1]
            if val_str == '':
                # nested mapping
                mapping = {}
                parent[key] = mapping
                stack.append((indent, mapping))
            else:
                # scalar mapping
                parent[key] = parse_scalar(val_str)
        return root
