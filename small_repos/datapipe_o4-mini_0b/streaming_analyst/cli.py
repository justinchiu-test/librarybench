import argparse
from pipeline import (
    scaffold_pipeline, run_pipeline, monitor_pipeline,
    debug_pipeline, enable_streaming, set_skip_on_error,
    set_rate_limit, start_prometheus_exporter
)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="stream-cli")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("scaffold_pipeline")
    run_p = sub.add_parser("run_pipeline")
    run_p.add_argument("--stream", action="store_true")

    sub.add_parser("monitor_pipeline")
    dbg = sub.add_parser("debug_pipeline")
    dbg.add_argument("record", type=str)

    sub.add_parser("enable_streaming")
    sub.add_parser("set_skip_on_error")
    rl = sub.add_parser("set_rate_limit")
    rl.add_argument("limit", type=int)

    sub.add_parser("start_prometheus_exporter")

    args = parser.parse_args(argv)
    if args.command == "scaffold_pipeline":
        print(scaffold_pipeline())
    elif args.command == "run_pipeline":
        p = run_pipeline(stream=args.stream)
        print(f"Pipeline running, stream={p.streaming_enabled}")
    elif args.command == "monitor_pipeline":
        # For stub, create a fresh pipeline
        p = run_pipeline(stream=True)
        print(monitor_pipeline(p))
    elif args.command == "debug_pipeline":
        # stub function for demo
        def identity(rec): return rec
        print(debug_pipeline(identity, args.record))
    elif args.command == "enable_streaming":
        p = run_pipeline(stream=True)
        enable_streaming(p)
        print(f"Streaming enabled: {p.streaming_enabled}")
    elif args.command == "set_skip_on_error":
        p = run_pipeline(stream=True)
        set_skip_on_error(p)
        print(f"Skip on error: {p.skip_on_error}")
    elif args.command == "set_rate_limit":
        p = run_pipeline(stream=True)
        set_rate_limit(p, args.limit)
        print(f"Rate limit: {p.rate_limit}")
    elif args.command == "start_prometheus_exporter":
        p = run_pipeline(stream=True)
        start_prometheus_exporter(p)
        print(f"Exporter started: {p.exporter_started}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
