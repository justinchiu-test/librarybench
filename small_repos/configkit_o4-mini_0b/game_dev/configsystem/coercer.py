class CustomCoercers:
    def __init__(self):
        self.coercers = {}

    def register(self, key_suffix, fn):
        self.coercers[key_suffix] = fn

    def apply(self, cfg):
        def walk(path, node):
            if isinstance(node, dict):
                for k, v in node.items():
                    node[k] = walk(path + [k], v)
            elif isinstance(node, list):
                return [walk(path, v) for v in node]
            else:
                for suffix, fn in self.coercers.items():
                    if path and path[-1].endswith(suffix):
                        try:
                            return fn(node)
                        except Exception:
                            pass
                return node
            return node
        walk([], cfg)
