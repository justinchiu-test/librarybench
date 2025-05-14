import argparse
import sys
import json
import os
from .snapshot import take_snapshot, diff_snapshots
from .config import load_config
from .logger import setup_logger
from .filters import FilterRules

def main():
    parser = argparse.ArgumentParser(prog='watcher')
    sub = parser.add_subparsers(dest='cmd')

    p_snap = sub.add_parser('snapshot')
    p_snap.add_argument('dir')
    p_snap.add_argument('--config', help='Config file path')

    p_diff = sub.add_parser('diff')
    p_diff.add_argument('old', help='Old snapshot JSON')
    p_diff.add_argument('new', help='New snapshot JSON')
    p_diff.add_argument('--dir', help='Base directory')
    p_diff.add_argument('--hash', action='store_true')

    args = parser.parse_args()
    if args.cmd == 'snapshot':
        cfg = {}
        if args.config:
            cfg = load_config(args.config)
        fr = FilterRules(
            include=cfg.get('include'),
            exclude=cfg.get('exclude'),
            hide_dotfiles=cfg.get('hide_dotfiles', True)
        )
        snap = take_snapshot(args.dir, filter_func=fr.match)
        print(json.dumps(snap))
    elif args.cmd == 'diff':
        with open(args.old) as f:
            old = json.load(f)
        with open(args.new) as f:
            new = json.load(f)
        diff = diff_snapshots(old, new, directory=args.dir, hash_compare=args.hash)
        print(json.dumps(diff))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
