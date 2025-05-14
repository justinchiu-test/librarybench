class CLIConfigGenerator:
    def __init__(self, schema):
        self.schema = schema or {}

    def generate(self):
        opts = []
        for key in self.schema:
            opt = f"--{key}=<value>"
            opts.append(opt)
        return opts
