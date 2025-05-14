import argparse

class CLIManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="pipeline")
        sub = self.parser.add_subparsers(dest='command')
        sub.add_parser('bootstrap', help='Bootstrap new market feed')
        sub.add_parser('backfill', help='Run backfill')
        sub.add_parser('status', help='Inspect pipeline status')

    def run(self, args=None):
        parsed = self.parser.parse_args(args)
        cmd = parsed.command
        if cmd == 'bootstrap':
            return 0
        elif cmd == 'backfill':
            return 0
        elif cmd == 'status':
            return 0
        else:
            self.parser.print_help()
            return 1
