import argparse
import asyncio
import logging
import signal
import sys
from .watcher import AsyncFileWatcher
from .webhook import WebhookIntegration

def parse_args():
    parser = argparse.ArgumentParser(description="Async File Watcher CLI")
    parser.add_argument("paths", nargs="+", help="Paths to watch")
    parser.add_argument("--include", action="append", help="Include pattern", default=[])
    parser.add_argument("--exclude", action="append", help="Exclude pattern", default=[])
    parser.add_argument("--webhook", action="append", help="Webhook URL", default=[])
    parser.add_argument("--interval", type=float, help="Polling interval seconds", default=1.0)
    parser.add_argument("--logfile", help="Log file path", default=None)
    parser.add_argument("--loglevel", help="Log level", default="INFO")
    return parser.parse_args()

def setup_logging(logfile: str, level: str):
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if logfile:
        fh = logging.FileHandler(logfile)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger

async def main():
    args = parse_args()
    logger = setup_logging(args.logfile, args.loglevel)
    watcher = AsyncFileWatcher(
        paths=args.paths,
        includes=args.include or None,
        excludes=args.exclude or None,
        interval=args.interval,
    )
    # print events to console
    def print_handler(event):
        logger.info(f"Event: {event}")
    watcher.register_handler(print_handler)
    if args.webhook:
        webhook = WebhookIntegration(args.webhook, logger=logger)
        watcher.register_handler(webhook.send)
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    def _signal_handler():
        stop_event.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)
    await watcher.start()
    await stop_event.wait()
    await watcher.stop()

if __name__ == "__main__":
    asyncio.run(main())
