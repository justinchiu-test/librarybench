import os
import sys
import argparse
from .version import get_version, bump_version
from .scaffold import gen_scaffold
from .publish import publish_package
from .config_schema import generate_schema
from .config_validator import validate_config
from .help_formatter import format_help
from .i18n import load_translations
from .signals import handle_signals
from .di import init_di, inject
from .config_parser import parse_config_files
from .secrets import manage_secrets

def extract(args):
    return {'action': 'extract', 'param': args.param}

def transform(args):
    return {'action': 'transform', 'param': args.param}

def load(args):
    return {'action': 'load', 'param': args.param}

def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', help='Show version')
    subparsers = parser.add_subparsers(dest='command')
    for name, func in [('extract', extract), ('transform', transform), ('load', load)]:
        sp = subparsers.add_parser(name)
        sp.add_argument('--param', default='default')
        sp.set_defaults(func=func)
    args = parser.parse_args(argv)
    # handle version
    if args.version:
        print(get_version())
        return
    # env override
    for key in vars(args):
        env_key = key.upper()
        if env_key in os.environ:
            val = os.environ[env_key]
            # type cast to str/int if possible
            dest = getattr(args, key)
            try:
                val = type(dest)(val)
            except Exception:
                pass
            setattr(args, key, val)
    if hasattr(args, 'func'):
        result = args.func(args)
        print(result)
        return result
    parser.print_help()
