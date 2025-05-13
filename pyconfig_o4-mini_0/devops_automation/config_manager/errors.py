class ConfigError(Exception):
    def __init__(self, path=None, line=None, context=None, msg=None):
        self.path = path
        self.line = line
        self.context = context
        self.msg = msg or ""
        super().__init__(self.msg)

    def __str__(self):
        parts = [self.msg]
        if self.path:
            parts.append(f"path={self.path}")
        if self.line is not None:
            parts.append(f"line={self.line}")
        if self.context:
            parts.append(f"context={self.context}")
        return "; ".join(parts)
