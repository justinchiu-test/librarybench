import argparse
import json
import sys
from fintech_compliance_officer.queue import TaskQueue

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    p_enq = subparsers.add_parser('enqueue')
    p_enq.add_argument('--payload', required=True)
    p_enq.add_argument('--delay', type=int, default=0)
    p_cancel = subparsers.add_parser('cancel')
    p_cancel.add_argument('--id', required=True)
    subparsers.add_parser('metrics')
    subparsers.add_parser('logs')
    args = parser.parse_args()
    q = TaskQueue('cli_key')
    if args.command == 'enqueue':
        payload = json.loads(args.payload)
        task_id = q.enqueue(payload, args.delay)
        print(task_id)
    elif args.command == 'cancel':
        ok = q.cancel_task(args.id)
        print('cancelled' if ok else 'not found')
    elif args.command == 'metrics':
        print(json.dumps(q.get_metrics()))
    elif args.command == 'logs':
        print(json.dumps(q.get_audit_log()))
    else:
        parser.print_help()
        sys.exit(1)
