import argparse
import os
import json
from statemachine import StateMachine

def scaffold_machine(name):
    filename = f"{name}.py"
    content = (
        "from statemachine import StateMachine\n\n"
        "def create_machine():\n"
        "    m = StateMachine()\n"
        "    # define your states and transitions here\n"
        "    return m\n"
    )
    with open(filename, "w") as f:
        f.write(content)
    return filename

def visualize_machine(file_path):
    # assume JSON file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")
    with open(file_path, "r") as f:
        data = f.read()
    m = StateMachine.load_machine(data)
    out = f"{file_path}.dot"
    m.export_visualization(out)
    return out

def main():
    parser = argparse.ArgumentParser(prog="cli")
    sub = parser.add_subparsers(dest="cmd")
    sc = sub.add_parser("scaffold")
    sc.add_argument("machine_name")
    vis = sub.add_parser("visualize")
    vis.add_argument("machine_file")
    args = parser.parse_args()
    if args.cmd == "scaffold":
        scaffold_machine(args.machine_name)
    elif args.cmd == "visualize":
        visualize_machine(args.machine_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
