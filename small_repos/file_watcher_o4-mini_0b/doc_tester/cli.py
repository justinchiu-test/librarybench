import argparse
import sys
from watcher import Watcher

def main():
    parser = argparse.ArgumentParser(description="Start documentation watcher")
    parser.add_argument("paths", nargs="+", help="Paths to watch")
    parser.add_argument("--include", action="append", help="Include pattern (fnmatch)")
    parser.add_argument("--exclude", action="append", help="Exclude pattern (fnmatch)")
    parser.add_argument("--endpoint", action="append", required=True, help="Webhook endpoint URL")
    args = parser.parse_args()
    watcher = Watcher(args.paths, args.endpoint, args.include, args.exclude)
    watcher.start()

if __name__ == "__main__":
    main()
