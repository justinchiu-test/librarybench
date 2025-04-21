#!/usr/bin/env python
import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

from package_manager import PackageManager, DependencyError, VersionConflictError


def load_registry(file_path: Optional[str] = None) -> Dict[Tuple[str, str], List[str]]:
    """
    Load package registry from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing package registry
        
    Returns:
        Dict: Dictionary mapping (name, version) to dependencies
    """
    if not file_path or not os.path.exists(file_path):
        return {}
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        registry = {}
        # Convert from JSON format to internal format
        for pkg_name, versions in data.items():
            for version, deps in versions.items():
                registry[(pkg_name, version)] = deps
                
        return registry
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading registry: {e}", file=sys.stderr)
        return {}


def save_registry(registry: Dict[Tuple[str, str], List[str]], file_path: str) -> None:
    """
    Save package registry to a JSON file.
    
    Args:
        registry: Dictionary mapping (name, version) to dependencies
        file_path: Path to save the JSON file
    """
    try:
        # Convert from internal format to JSON format
        data = {}
        for (pkg_name, version), deps in registry.items():
            if pkg_name not in data:
                data[pkg_name] = {}
            data[pkg_name][version] = deps
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Registry saved to {file_path}")
    except Exception as e:
        print(f"Error saving registry: {e}", file=sys.stderr)


def main() -> None:
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="Lightweight package manager with versioning and environments."
    )
    
    # Add global arguments
    parser.add_argument(
        "--registry", 
        "-r", 
        help="Path to the package registry JSON file", 
        default="registry.json"
    )
    parser.add_argument(
        "--environment",
        "-e",
        help="Environment to use",
        default=None
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Registry commands
    registry_parser = subparsers.add_parser("registry", help="Manage package registry")
    registry_subparsers = registry_parser.add_subparsers(dest="registry_command", help="Registry command")
    
    # Add to registry
    add_registry_parser = registry_subparsers.add_parser("add", help="Add package to registry")
    add_registry_parser.add_argument("name", help="Package name")
    add_registry_parser.add_argument("version", help="Package version")
    add_registry_parser.add_argument(
        "--dependencies",
        "-dep",
        nargs="+",
        help="Dependencies for the package",
        default=[]
    )
    
    # List registry
    registry_subparsers.add_parser("list", help="List packages in registry")
    
    # Environment commands
    env_parser = subparsers.add_parser("env", help="Manage environments")
    env_subparsers = env_parser.add_subparsers(dest="env_command", help="Environment command")
    
    # Create environment
    create_env_parser = env_subparsers.add_parser("create", help="Create a new environment")
    create_env_parser.add_argument("name", help="Environment name")
    
    # Use environment
    use_env_parser = env_subparsers.add_parser("use", help="Use an environment")
    use_env_parser.add_argument("name", help="Environment name")
    
    # List environments
    env_subparsers.add_parser("list", help="List environments")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package specification (e.g., 'package==1.0')")
    
    # Install from lockfile
    install_lock_parser = subparsers.add_parser("install-lockfile", help="Install from lockfile")
    install_lock_parser.add_argument("lockfile", help="Path to lockfile")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a package")
    remove_parser.add_argument("package", help="Package name to remove")
    remove_parser.add_argument("--version", "-v", help="Package version to remove")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed packages")
    list_parser.add_argument("--environment", "-e", help="Environment to list packages from")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if a package is installed")
    check_parser.add_argument("package", help="Package name to check")
    check_parser.add_argument("--version", "-v", help="Package version to check")
    
    # Generate lockfile
    lock_parser = subparsers.add_parser("lock", help="Generate lockfile")
    lock_parser.add_argument("--environment", "-e", help="Environment to generate lockfile for")
    lock_parser.add_argument("--output", "-o", help="Output file path")
    
    # Find packages
    find_parser = subparsers.add_parser("find", help="Find packages in registry")
    find_parser.add_argument("package", help="Package name to find")
    find_parser.add_argument("--version-spec", "-v", help="Version specification (e.g., '>=1.0,<2.0')")
    
    # Why package
    why_parser = subparsers.add_parser("why", help="Explain why a package was installed")
    why_parser.add_argument("package", help="Package name")
    why_parser.add_argument("--version", "-v", help="Package version")
    
    args = parser.parse_args()
    
    # Initialize package manager
    pm = PackageManager()
    
    # Load package registry
    registry = load_registry(args.registry)
    for (pkg_name, version), deps in registry.items():
        pm.add_to_registry(pkg_name, version, deps)
    
    # Use specified environment if provided
    if args.environment:
        try:
            pm.use_env(args.environment)
        except ValueError:
            print(f"Creating environment: {args.environment}")
            pm.create_env(args.environment)
            pm.use_env(args.environment)
    
    try:
        # Handle registry commands
        if args.command == "registry":
            if args.registry_command == "add":
                pm.add_to_registry(args.name, args.version, args.dependencies)
                print(f"Added {args.name}=={args.version} to registry")
                save_registry(pm._registry, args.registry)
            elif args.registry_command == "list":
                print("Available packages in registry:")
                registry_data = {}
                for (name, version), deps in pm._registry.items():
                    if name not in registry_data:
                        registry_data[name] = []
                    registry_data[name].append(version)
                
                for name, versions in sorted(registry_data.items()):
                    versions_str = ", ".join(sorted(versions))
                    print(f"  - {name}: {versions_str}")
            else:
                parser.parse_args(["registry", "--help"])
        
        # Handle environment commands
        elif args.command == "env":
            if args.env_command == "create":
                pm.create_env(args.name)
                print(f"Environment '{args.name}' created")
            elif args.env_command == "use":
                pm.use_env(args.name)
                print(f"Using environment '{args.name}'")
            elif args.env_command == "list":
                print("Available environments:")
                for env_name in pm._environments:
                    current = " (current)" if env_name == pm._current_env else ""
                    print(f"  - {env_name}{current}")
            else:
                parser.parse_args(["env", "--help"])
        
        # Handle install command
        elif args.command == "install":
            pm.install(args.package)
            print(f"Package '{args.package}' installed successfully.")
            
        # Handle install-lockfile command
        elif args.command == "install-lockfile":
            pm.install_from_lockfile(args.lockfile)
            print(f"Packages installed from lockfile: {args.lockfile}")
            
        # Handle remove command
        elif args.command == "remove":
            pm.remove_package(args.package, args.version)
            print(f"Package '{args.package}' removed successfully.")
            
        # Handle list command
        elif args.command == "list":
            installed = pm.list_packages(args.environment)
            env_name = args.environment or pm._current_env
            
            if installed:
                print(f"Installed packages in environment '{env_name}':")
                for name, version in sorted(installed):
                    deps = pm.get_dependencies(name, version)
                    deps_str = ", ".join(deps) if deps else "none"
                    print(f"  - {name}=={version} (dependencies: {deps_str})")
            else:
                print(f"No packages installed in environment '{env_name}'.")
            
        # Handle check command
        elif args.command == "check":
            if pm.is_installed(args.package, args.version):
                version_str = f"=={args.version}" if args.version else ""
                deps = pm.get_dependencies(args.package, args.version)
                deps_str = ", ".join(deps) if deps else "none"
                print(f"Package '{args.package}{version_str}' is installed (dependencies: {deps_str}).")
            else:
                version_str = f"=={args.version}" if args.version else ""
                print(f"Package '{args.package}{version_str}' is not installed.")
                
        # Handle lock command
        elif args.command == "lock":
            lockfile_path = pm.generate_lockfile(args.environment)
            if args.output:
                import shutil
                shutil.copy(lockfile_path, args.output)
                print(f"Lockfile generated at: {args.output}")
            else:
                print(f"Lockfile generated at: {lockfile_path}")
                
        # Handle find command
        elif args.command == "find":
            results = pm.find_package(args.package, args.version_spec or "")
            if results:
                print(f"Found versions of '{args.package}':")
                for name, version in sorted(results, key=lambda x: x[1]):
                    print(f"  - {name}=={version}")
            else:
                version_spec = f" matching '{args.version_spec}'" if args.version_spec else ""
                print(f"No versions of '{args.package}'{version_spec} found in registry.")
                
        # Handle why command
        elif args.command == "why":
            try:
                reason = pm.why(args.package, args.version)
                version_str = f"=={args.version}" if args.version else ""
                print(f"Package '{args.package}{version_str}' was installed because: {reason}")
            except KeyError:
                version_str = f"=={args.version}" if args.version else ""
                print(f"Package '{args.package}{version_str}' is not installed.")
                
        else:
            parser.print_help()
            
    except DependencyError as e:
        print(f"Dependency error: {e}", file=sys.stderr)
        sys.exit(1)
    except VersionConflictError as e:
        print(f"Version conflict: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Package not found: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()