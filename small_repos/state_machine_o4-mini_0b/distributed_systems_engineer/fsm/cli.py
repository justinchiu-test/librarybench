import argparse
import sys

def build_workflow(args):
    print(f"Building workflow {args.name}")

def simulate(args):
    print(f"Simulating workflow {args.name}")

def visualize(args):
    print(f"Visualizing workflow {args.name}")

def cli():
    parser = argparse.ArgumentParser(prog='fsm')
    sub = parser.add_subparsers(dest='cmd')
    b = sub.add_parser('build')
    b.add_argument('name')
    b.set_defaults(func=build_workflow)
    s = sub.add_parser('simulate')
    s.add_argument('name')
    s.set_defaults(func=simulate)
    v = sub.add_parser('visualize')
    v.add_argument('name')
    v.set_defaults(func=visualize)
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    cli()
