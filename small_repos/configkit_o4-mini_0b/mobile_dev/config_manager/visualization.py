class ConfigVisualization:
    def __init__(self, data):
        self.data = data

    def render(self):
        lines = []
        def recurse(node, prefix=''):
            if isinstance(node, dict):
                for key, val in node.items():
                    lines.append(f"{prefix}{key}")
                    recurse(val, prefix + '  ')
        recurse(self.data)
        return "\n".join(lines)
