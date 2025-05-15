import os
import shutil

def gen_scaffold(output_dir, project_name, use_pyproject=False):
    """
    Generate a project scaffold
    
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
        f.write(f"# {project_name}\n\nA new project.\n")
    
    if use_pyproject:
        # Create pyproject.toml
        with open(os.path.join(output_dir, "pyproject.toml"), "w") as f:
            f.write(f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A new project"
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
    cli_dir = os.path.join(package_dir, "cli.py")
    with open(cli_dir, "w") as f:
        f.write("""import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Command line tool")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(__version__)
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")