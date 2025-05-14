import argparse
import json
import sys
from .config import ConfigFileSupport
from .history import RetryHistoryCollector

def main():
    parser = argparse.ArgumentParser(prog='retry-cli')
    sub = parser.add_subparsers(dest='command')
    validate = sub.add_parser('validate')
    validate.add_argument('config')
    simulate = sub.add_parser('simulate')
    simulate.add_argument('config')
    args = parser.parse_args()
    if args.command == 'validate':
        conf = ConfigFileSupport.load(args.config)
        print(json.dumps(conf))
    elif args.command == 'simulate':
        conf = ConfigFileSupport.load(args.config)
        hist = RetryHistoryCollector()
        # Simulate one successful attempt
        hist.record(0, 0, None, True)
        print(f"Simulated {len(hist.attempts)} attempts")
    else:
        parser.print_help()
        sys.exit(1)
