import argparse
import json
from .snapshot import Snapshot

def main():
    parser = argparse.ArgumentParser(description="Quick directory audit")
    parser.add_argument('root', help="Root directory to scan")
    args = parser.parse_args()
    snap = Snapshot(args.root).take()
    print(json.dumps(snap, indent=2))

if __name__ == '__main__':
    main()
