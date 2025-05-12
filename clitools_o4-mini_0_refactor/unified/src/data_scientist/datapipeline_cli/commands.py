"""
CLI commands for data scientists.
"""
import os
import argparse
from .version import get_version

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true')
    subparsers = parser.add_subparsers(dest='action')
    # extract command
    extract = subparsers.add_parser('extract')
    extract.add_argument('--param', default=None)
    args = parser.parse_args(argv)
    # handle version
    if args.version:
        v = get_version()
        print(v)
        return None
    # get parameters
    action = args.action
    param = args.param
    if param is None:
        param = os.environ.get('PARAM')
    result = {'action': action, 'param': param}
    print(result)
    return result