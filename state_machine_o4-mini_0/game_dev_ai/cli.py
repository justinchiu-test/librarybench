import argparse
import json

def scaffold_machine(args):
    data = {'name': args.name, 'states': [], 'transitions': []}
    print(json.dumps(data))

def simulate(args):
    print(f"Simulating route with {args.steps} steps")

def export_graph(args):
    print(f"Exporting graph to {args.output}")

def main():
    parser = argparse.ArgumentParser(prog='npc_tool')
    sub = parser.add_subparsers(dest='command')
    p1 = sub.add_parser('scaffold')
    p1.add_argument('--name', required=True)
    p1.set_defaults(func=scaffold_machine)
    p2 = sub.add_parser('simulate')
    p2.add_argument('--steps', type=int, default=10)
    p2.set_defaults(func=simulate)
    p3 = sub.add_parser('export')
    p3.add_argument('--output', required=True)
    p3.set_defaults(func=export_graph)
    args = parser.parse_args()
    args.func(args)
