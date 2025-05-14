import argparse
import sys
from pipeline.batch import run_batch
from pipeline.stream import run_streaming
from pipeline.metrics import export_prometheus_metrics

def main():
    parser = argparse.ArgumentParser(description="Pipeline CLI")
    subparsers = parser.add_subparsers(dest='command')

    batch_parser = subparsers.add_parser('batch')
    batch_parser.add_argument('--input', nargs='+', help='Batch input records')

    stream_parser = subparsers.add_parser('stream')
    stream_parser.add_argument('--input', nargs='+', help='Stream input records')
    stream_parser.add_argument('--max-events', type=int, default=None, help='Max events to process')

    subparsers.add_parser('metrics')

    args = parser.parse_args()

    if args.command == 'batch':
        def proc(x): print(f"Processing {x}")
        metrics = run_batch(proc, args.input or [])
        print(metrics)
    elif args.command == 'stream':
        def generator():
            for x in args.input or []:
                yield x
        def proc(x): print(f"Processing {x}")
        metrics = run_streaming(generator(), proc, max_events=args.max_events)
        print(metrics)
    elif args.command == 'metrics':
        print(export_prometheus_metrics())
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
