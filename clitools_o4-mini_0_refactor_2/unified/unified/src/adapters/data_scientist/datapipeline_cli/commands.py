"""
Command-line interface entrypoint for data_scientist datapipeline CLI.
"""
import argparse
import os
from .version import get_version

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', help='show version')
    parser.add_argument('action', nargs='?', help='action to perform')
    parser.add_argument('--param', default=os.getenv('PARAM'), help='parameter')
    args = parser.parse_args(argv)
    if args.version:
        ver = get_version()
        print(ver)
        return
    res = {'action': args.action, 'param': args.param}
    print(res)
    return res