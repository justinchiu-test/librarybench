class ConfigError(Exception):
    def __init__(self, message, file, line):
        super().__init__(f"{message} ({file}:{line})")
        self.message = message
        self.file = file
        self.line = line
