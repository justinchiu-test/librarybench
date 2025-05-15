import os
import shutil

def gen_scaffold(output_dir, project_name, use_pyproject=False):
    """
    Generate a project scaffold for operations tools
    
    Args:
        output_dir: Output directory path
        project_name: Name of the project
        use_pyproject: Whether to use pyproject.toml (True) or setup.py (False)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create package directory
    package_dir = os.path.join(output_dir, project_name)
    os.makedirs(package_dir, exist_ok=True)
    
    # Create config directory
    config_dir = os.path.join(output_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create tests directory
    tests_dir = os.path.join(output_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    
    # Create __init__.py in package dir
    with open(os.path.join(package_dir, "__init__.py"), "w") as f:
        f.write(f'__version__ = "0.1.0"\n')
    
    # Create tests/__init__.py
    with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
        f.write("")
    
    # Create README.md
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write(f"# {project_name}\n\nAn operations tool.\n")
    
    # Create default config.yaml
    with open(os.path.join(config_dir, "config.yaml"), "w") as f:
        f.write("""# Default configuration
service:
  name: sample-service
  port: 8080
  log_level: info
  
deployment:
  replicas: 1
  memory: 512Mi
  cpu: 0.5
""")
    
    if use_pyproject:
        # Create pyproject.toml
        with open(os.path.join(output_dir, "pyproject.toml"), "w") as f:
            f.write(f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "An operations tool"
requires-python = ">=3.7"

[project.scripts]
{project_name} = "{project_name}.cli:main"

[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
""")
    else:
        # Create setup.py
        with open(os.path.join(output_dir, "setup.py"), "w") as f:
            f.write(f"""from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(),
    entry_points={{
        "console_scripts": [
            "{project_name}={project_name}.cli:main",
        ],
    }},
)
""")
    
    # Create a basic CLI module
    with open(os.path.join(package_dir, "cli.py"), "w") as f:
        f.write("""import sys
import argparse
import yaml

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Operations CLI tool")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy service")
    deploy_parser.add_argument("--env", default="dev", help="Environment name")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check service status")
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(__version__)
        return 0
        
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        return 1
    
    if args.command == "deploy":
        print(f"Deploying to {args.env} environment")
    elif args.command == "status":
        print("Checking service status")
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")