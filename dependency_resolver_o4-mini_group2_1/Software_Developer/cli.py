import argparse
import json
import sys
from env_manager import EnvironmentManager
from repo_manager import RepositoryManager
from solver import DependencySolver

def setup_parser():
    parser = argparse.ArgumentParser(prog="pkgmgr")
    sub = parser.add_subparsers(dest="cmd")

    # env commands
    p_env = sub.add_parser("env")
    e_sub = p_env.add_subparsers(dest="env_cmd")
    p_import = e_sub.add_parser("import")
    p_import.add_argument("config", help="Path to environment config JSON")
    p_delete = e_sub.add_parser("delete")
    p_delete.add_argument("name", help="Environment name to delete")
    e_sub.add_parser("list")

    # repo commands
    p_repo = sub.add_parser("repo")
    r_sub = p_repo.add_subparsers(dest="repo_cmd")
    p_radd = r_sub.add_parser("add")
    p_radd.add_argument("name")
    p_radd.add_argument("packages", help="JSON string of packages dict")
    r_sub.add_parser("remove").add_argument("name")
    r_sub.add_parser("list")

    # solve
    p_solve = sub.add_parser("solve")
    p_solve.add_argument("constraints", help="JSON string of constraints dict")

    return parser

def print_help(parser):
    parser.print_help()
    return 1

def handle_env(args, parser, em):
    if args.env_cmd == "import":
        print(em.import_env(args.config))
    elif args.env_cmd == "delete":
        em.delete_env(args.name)
    elif args.env_cmd == "list":
        print(json.dumps(em.list_envs()))
    else:
        return print_help(parser)
    return 0

def handle_repo(args, parser, rm):
    if args.repo_cmd == "add":
        rm.add_repo(args.name, json.loads(args.packages))
    elif args.repo_cmd == "remove":
        rm.remove_repo(args.name)
    elif args.repo_cmd == "list":
        print(json.dumps(rm.list_repos()))
    else:
        return print_help(parser)
    return 0

def handle_solve(args, ds):
    constraints = json.loads(args.constraints)
    print(json.dumps(ds.solve(constraints)))
    return 0

def main(argv=None):
    parser = setup_parser()
    args = parser.parse_args(argv)
    em = EnvironmentManager()
    rm = RepositoryManager()
    ds = DependencySolver(rm)

    if args.cmd == "env":
        return handle_env(args, parser, em)
    elif args.cmd == "repo":
        return handle_repo(args, parser, rm)
    elif args.cmd == "solve":
        return handle_solve(args, ds)
    else:
        return print_help(parser)

if __name__ == "__main__":
    sys.exit(main())
