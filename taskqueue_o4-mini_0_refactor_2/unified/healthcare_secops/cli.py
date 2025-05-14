import sys
import argparse
from healthcare_secops.pipeline.audit import AuditLogging
from healthcare_secops.pipeline.task import UniqueTaskID

auditor = AuditLogging()
task_manager = UniqueTaskID()

def main(argv=None):
    parser = argparse.ArgumentParser(description="CLI for pipeline")
    sub = parser.add_subparsers(dest='command')
    p_enq = sub.add_parser('enqueue')
    p_enq.add_argument('--task-id', help='Task ID')
    p_cancel = sub.add_parser('cancel')
    p_cancel.add_argument('--task-id', help='Task ID')
    sub.add_parser('tail-logs')
    args = parser.parse_args(argv)
    if args.command == 'enqueue':
        tid = args.task_id or task_manager.generate()
        auditor.log('enqueue', tid)
        print(f"Enqueued {tid}")
    elif args.command == 'cancel':
        if not args.task_id:
            print("Task ID required", file=sys.stderr)
            return 1
        auditor.log('cancel', args.task_id)
        print(f"Cancelled {args.task_id}")
    elif args.command == 'tail-logs':
        logs = auditor.read_logs()
        for entry in logs:
            print(entry)
    else:
        parser.print_help()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
