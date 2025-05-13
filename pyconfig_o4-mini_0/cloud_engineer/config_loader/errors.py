# error_reporting
class ConfigError(Exception):
    def __init__(self, message: str, file: str = None, line: int = None, context: str = None):
        super().__init__(message)
        self.file = file
        self.line = line
        self.context = context

    def __str__(self):
        parts = [super().__str__()]
        if self.file is not None and self.line is not None:
            parts.append(f" ({self.file}:{self.line})")
        if self.context:
            parts.append(f" Context: {self.context}")
        return "".join(parts)
