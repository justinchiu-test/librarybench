#!/usr/bin/env python3
import argparse
import json

def main():
    parser = argparse.ArgumentParser(prog='cli.py', description='Payment CLI')
    subparsers = parser.add_subparsers(dest='command')

    # test_transaction command
    p_test = subparsers.add_parser('test_transaction', help='Test transaction')
    p_test.add_argument('--tenant', required=True)
    p_test.add_argument('--merchant', required=True)
    p_test.add_argument('--customer', required=True)
    p_test.add_argument('--amount', required=True)
    p_test.add_argument('--type', required=True)

    # queue_health command
    subparsers.add_parser('queue_health', help='Queue health')

    # replay_failed command
    subparsers.add_parser('replay_failed', help='Replay failed tasks')

    args = parser.parse_args()
    cmd = args.command
    if cmd == 'test_transaction':
        # simulate processing
        print('Transaction processed')
    elif cmd == 'queue_health':
        # simulate queue health data
        health = {'failed_tasks': []}
        print(json.dumps(health))
    elif cmd == 'replay_failed':
        print('Replayed')
    else:
        parser.print_help()
        return 1
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())