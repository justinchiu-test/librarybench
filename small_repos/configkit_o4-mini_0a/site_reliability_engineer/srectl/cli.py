import argparse

class CLIConfigGenerator:
    def __init__(self, config):
        self.config = config
        self.parser = argparse.ArgumentParser()
        flat = self._flatten(config)
        for key in flat:
            dest = key.replace('.', '_')
            self.parser.add_argument(f"--{key}", dest=dest, type=str)

    @staticmethod
    def _flatten(d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(CLIConfigGenerator._flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    def get_parser(self):
        return self.parser
