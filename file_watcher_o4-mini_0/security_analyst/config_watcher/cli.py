import argparse
import asyncio
import logging
from .logging_support import setup_logging
from .webhook_integration import WebhookClient
from .filter_rules import FilterRules
from .watcher import ConfigWatcher

def main():
    parser = argparse.ArgumentParser(description="Config policy watcher")
    parser.add_argument('paths', nargs='+', help="Paths to watch")
    parser.add_argument('--include', action='append', help="Include pattern")
    parser.add_argument('--exclude', action='append', help="Exclude pattern")
    parser.add_argument('--log-file', help="Log file path")
    parser.add_argument('--log-level', default='INFO', help="Log level")
    parser.add_argument('--remote-log', help="Remote log HTTP URL")
    parser.add_argument('--webhook-url', required=True, help="Webhook URL")
    args = parser.parse_args()
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger = setup_logging(level=log_level, log_file=args.log_file, remote_url=args.remote_log)
    webhook = WebhookClient(args.webhook_url)
    filters = FilterRules()
    if args.include:
        for p in args.include:
            filters.include(p)
    if args.exclude:
        for p in args.exclude:
            filters.exclude(p)
    watcher = ConfigWatcher(args.paths, webhook, logger, filters)

    # Ensure we have a usable event loop (pytest plugin may have closed the default)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(watcher.start())
    except KeyboardInterrupt:
        pass
