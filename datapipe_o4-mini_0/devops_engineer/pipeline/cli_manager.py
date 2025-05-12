import argparse

class CLIManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="pipeline")
        sub = self.parser.add_subparsers(dest='cmd')
        sub.add_parser('deploy')
        sub.add_parser('upgrade')
        sub.add_parser('rollback')
        sub.add_parser('debug')

    def run(self, args=None):
        ns = self.parser.parse_args(args)
        return ns.cmd
