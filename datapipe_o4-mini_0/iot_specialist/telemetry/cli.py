import argparse

registered_devices = set()

def register_device(device_id):
    registered_devices.add(device_id)
    return True

def backfill(start, end):
    return {'start': start, 'end': end, 'status': 'backfill_complete'}

def trace(stream):
    # stream: list of messages
    return stream[:5]

def cli_manager(args=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')
    p1 = sub.add_parser('register')
    p1.add_argument('device_id')
    p2 = sub.add_parser('backfill')
    p2.add_argument('start')
    p2.add_argument('end')
    p3 = sub.add_parser('trace')
    p3.add_argument('stream', nargs='+')
    parsed = parser.parse_args(args)
    if parsed.cmd == 'register':
        return register_device(parsed.device_id)
    if parsed.cmd == 'backfill':
        return backfill(parsed.start, parsed.end)
    if parsed.cmd == 'trace':
        return trace(parsed.stream)
    return None
