import argparse
import asyncio
from .filter_rules import DynamicFilterRules
from .event_detection import HighLevelEventDetection
from .async_api import AsyncIOAPI

class CLIInterface:
    def __init__(self, args=None):
        self.args = args

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Watch directories for file events")
        parser.add_argument('roots', nargs='+', help="Root directories to watch")
        parser.add_argument('--include', action='append', default=[], help="Include patterns")
        parser.add_argument('--exclude', action='append', default=[], help="Exclude patterns")
        return parser.parse_args(self.args)

    async def run(self):
        opts = self.parse_args()
        rules = DynamicFilterRules()
        for pat in opts.include:
            rules.add_include(pat)
        for pat in opts.exclude:
            rules.add_exclude(pat)
        detector = HighLevelEventDetection()
        api = AsyncIOAPI(opts.roots, rules, detector)
        events = []
        async for ev in api.watch():
            print(ev)
            events.append(ev)
        return events

def main(args=None):
    cli = CLIInterface(args)
    return asyncio.run(cli.run())
