import re
from collections.abc import Mapping

class DotNotationAccess:
    @staticmethod
    def get(cfg, path, default=None):
        parts = path.split('.')
        node = cfg
        for p in parts:
            if isinstance(node, Mapping) and p in node:
                node = node[p]
            else:
                return default
        return node

    @staticmethod
    def set(cfg, path, value):
        parts = path.split('.')
        node = cfg
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = value

class NestedMerge:
    @staticmethod
    def merge(a, b, conflicts=None):
        if conflicts is None:
            conflicts = []
        result = {}
        keys = set(a.keys()) | set(b.keys())
        for k in keys:
            va = a.get(k)
            vb = b.get(k)
            if k in a and k in b:
                if isinstance(va, dict) and isinstance(vb, dict):
                    before = len(conflicts)
                    merged_child = NestedMerge.merge(va, vb, conflicts)
                    result[k] = merged_child
                    # if any child conflict occurred, record this key as conflicted
                    if len(conflicts) > before:
                        conflicts.append(k)
                elif isinstance(va, list) and isinstance(vb, list):
                    result[k] = va + vb
                else:
                    conflicts.append(k)
                    result[k] = vb
            elif k in a:
                result[k] = va
            else:
                result[k] = vb
        return result

class VariableInterpolation:
    pattern = re.compile(r'\${([^}]+)}')
    @staticmethod
    def interpolate(cfg):
        from configsystem.utils import DotNotationAccess
        def resolver(s, seen=None):
            if seen is None:
                seen = set()
            def repl(m):
                key = m.group(1)
                if key in seen:
                    raise ValueError(f'Circular reference: {key}')
                seen.add(key)
                val = DotNotationAccess.get(cfg, key)
                if isinstance(val, str):
                    return resolver(val, seen)
                return str(val) if val is not None else ''
            return VariableInterpolation.pattern.sub(repl, s)
        def walk(node):
            if isinstance(node, dict):
                return {k: walk(v) for k, v in node.items()}
            elif isinstance(node, list):
                return [walk(v) for v in node]
            elif isinstance(node, str):
                return resolver(node)
            else:
                return node
        return walk(cfg)
