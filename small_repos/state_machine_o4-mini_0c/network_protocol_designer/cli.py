import argparse
import json
from protocol_dsl import load_machine, export_visualization

def scaffold_protocol(path='protocol_spec.json'):
    template = {
        'states': [],
        'transitions': [],
        'guards': [],
        'on_enter': {},
        'global_hooks': {},
        'history': {}
    }
    with open(path, 'w') as f:
        json.dump(template, f)
    print(f'Scaffolded protocol spec to {path}')

def visualize_spec(path):
    with open(path) as f:
        spec = f.read()
    load_machine(spec)
    dot = export_visualization('graphviz')
    print(dot)

def main():
    parser = argparse.ArgumentParser(prog='cli')
    subparsers = parser.add_subparsers(dest='command')

    scaffold = subparsers.add_parser('scaffold')
    scaffold.add_argument('target')

    visualize = subparsers.add_parser('visualize')
    visualize.add_argument('spec')

    args = parser.parse_args()
    if args.command == 'scaffold':
        if args.target == 'protocol':
            scaffold_protocol()
        else:
            scaffold_protocol(args.target)
    elif args.command == 'visualize':
        visualize_spec(args.spec)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
