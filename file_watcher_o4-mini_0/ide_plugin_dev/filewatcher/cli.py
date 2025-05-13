import asyncio
import argparse
import logging
from .watcher import FileWatcher
from .events import Event

def main():
    parser = argparse.ArgumentParser(description="FileWatcher CLI")
    subparsers = parser.add_subparsers(dest='command')

    sim = subparsers.add_parser('simulate', help='Simulate file event')
    sim.add_argument('--type', choices=['created','modified','deleted'], required=True)
    sim.add_argument('--path', required=True)
    sim.add_argument('--content', help='New content for modified event')

    args = parser.parse_args()
    logger = logging.getLogger('cli')
    watcher = FileWatcher('.', logger=logger)
    async def print_event(ev):
        print(ev)
    watcher.subscribe(print_event)

    async def run():
        if args.command == 'simulate':
            diff = None
            if args.type == 'modified':
                diff = args.content
            ev = Event(args.type, args.path, diff=diff)
            await watcher.simulate_event(ev)

    asyncio.run(run())

if __name__ == '__main__':
    main()
