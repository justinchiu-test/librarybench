import argparse
import sys
from env_manager import EnvironmentManager
from repository import RepositoryManager
from solver import DependencySolver, ConflictError

def main():
    parser = argparse.ArgumentParser(prog="envctl")
    subparsers = parser.add_subparsers(dest="command")

    # env commands
    env_parser = subparsers.add_parser("env", help="Manage environments")
    env_sub = env_parser.add_subparsers(dest="subcommand")
    env_import = env_sub.add_parser("import", help="Import environment from JSON file")
    env_import.add_argument("--file", "-f", required=True, help="Path to environment JSON")
    env_delete = env_sub.add_parser("delete", help="Delete an environment")
    env_delete.add_argument("name", help="Name of the environment to delete")
    env_list = env_sub.add_parser("list", help="List all environments")

    # repo commands
    repo_parser = subparsers.add_parser("repo", help="Manage repositories")
    repo_sub = repo_parser.add_subparsers(dest="subcommand")
    repo_add = repo_sub.add_parser("add", help="Add a repository")
    repo_add.add_argument("name", help="Repository name")
    repo_add.add_argument("url", help="Repository URL or local path")
    repo_remove = repo_sub.add_parser("remove", help="Remove a repository")
    repo_remove.add_argument("name", help="Repository name")
    repo_list = repo_sub.add_parser("list", help="List repositories")

    # install command
    install_parser = subparsers.add_parser("install", help="Install packages for environment")
    install_parser.add_argument("--env", required=True, help="Environment name")
    install_parser.add_argument(
        "--offline", action="store_true", help="Offline mode (use only local repos)"
    )

    args = parser.parse_args()

    # Default base_dir is taken from ENV_MANAGER_HOME or ~/.envmanager
    if args.command == "env":
        em = EnvironmentManager()
        if args.subcommand == "import":
            name = em.import_environment(args.file)
            print(f"Imported environment '{name}'.")
        elif args.subcommand == "delete":
            em.delete_environment(args.name)
            print(f"Deleted environment '{args.name}'.")
        elif args.subcommand == "list":
            for name in em.list_environments():
                print(name)
        else:
            parser.print_help()

    elif args.command == "repo":
        rm = RepositoryManager()
        if args.subcommand == "add":
            rm.add_repository(args.name, args.url)
            print(f"Added repository '{args.name}'.")
        elif args.subcommand == "remove":
            rm.remove_repository(args.name)
            print(f"Removed repository '{args.name}'.")
        elif args.subcommand == "list":
            for name, url in rm.list_repositories().items():
                print(f"{name}: {url}")
        else:
            parser.print_help()

    elif args.command == "install":
        em = EnvironmentManager()
        rm = RepositoryManager()
        try:
            env_conf = em.get_environment(args.env)
        except FileNotFoundError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        repo_urls = rm.get_repository_urls()
        solver = DependencySolver(repo_urls, offline=args.offline)
        try:
            plan = solver.solve(env_conf)
        except ConflictError as e:
            print(f"Conflict: {e}", file=sys.stderr)
            sys.exit(1)
        for pkg, ver in plan.items():
            print(f"{pkg}=={ver}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
