import argparse
import sys
import os
from taskqueue.queue import TaskQueue, _xor_decrypt

def main():
    # First, extract --data-dir flag and its value from sys.argv,
    # so that we accept it anywhere (before or after subcommand).
    data_dir = '.'
    args_list = []
    it = iter(sys.argv[1:])
    for arg in it:
        if arg == '--data-dir':
            # consume next as value
            try:
                data_dir = next(it)
            except StopIteration:
                # no value provided; keep default
                pass
        elif arg.startswith('--data-dir='):
            # form --data-dir=VALUE
            _, val = arg.split('=', 1)
            data_dir = val
        else:
            args_list.append(arg)

    # Ensure the data directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Path for CLI state snapshot
    snapshot_path = os.path.join(data_dir, 'snapshot.bin')

    # Restore existing queue state if present, else new
    if os.path.exists(snapshot_path):
        try:
            q = TaskQueue.restore(snapshot_path, data_dir=data_dir)
        except Exception:
            q = TaskQueue(data_dir=data_dir)
    else:
        q = TaskQueue(data_dir=data_dir)

    # Now parse the remaining args (subcommand and its args)
    parser = argparse.ArgumentParser(prog='taskcli')
    subparsers = parser.add_subparsers(dest='command')

    # enqueue
    p_enqueue = subparsers.add_parser('enqueue')
    p_enqueue.add_argument('payload')
    p_enqueue.add_argument('--delay', type=int, default=0)
    p_enqueue.add_argument('--max-retries', type=int, default=3)

    # stats
    subparsers.add_parser('stats')

    # cancel
    p_cancel = subparsers.add_parser('cancel')
    p_cancel.add_argument('task_id')

    # tail-logs
    subparsers.add_parser('tail-logs')

    args = parser.parse_args(args_list)
    args.data_dir = data_dir

    # Handle commands
    if args.command == 'enqueue':
        task_id = q.enqueue(
            args.payload,
            delay=getattr(args, 'delay', None),
            max_retries=getattr(args, 'max_retries', None)
        )
        print(task_id)
        # Persist the updated queue state
        q.snapshot(snapshot_path)

    elif args.command == 'stats':
        stats = q.get_stats()
        for k, v in stats.items():
            print(f'{k}: {v}')

    elif args.command == 'cancel':
        ok = q.cancel(args.task_id)
        print('Canceled' if ok else 'Not found')
        # Persist the updated queue state
        q.snapshot(snapshot_path)

    elif args.command == 'tail-logs':
        log_path = os.path.join(args.data_dir, 'audit.log')
        if not os.path.exists(log_path):
            # print empty (no logs)
            print('', end='')
            return
        # Read entire log, decrypt at once, then print
        with open(log_path, 'rb') as f:
            enc = f.read()
        dec = _xor_decrypt(enc, q.key)
        print(dec.decode(), end='')

    else:
        parser.print_help()
