import os

def gen_scaffold(path: str, name: str, use_pyproject: bool = False) -> None:
    """
    Generate a project scaffold for a new CLI application.
    
    Args:
        path: The directory where the project will be created
        name: The name of the project
        use_pyproject: Whether to use pyproject.toml instead of setup.py
    """
    # Create directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
        
    # Create package directory
    pkg_dir = os.path.join(path, name)
    if not os.path.exists(pkg_dir):
        os.makedirs(pkg_dir)
        
    # Create __init__.py in package directory
    with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
        f.write(f'"""Package {name}."""\n\n__version__ = "0.1.0"\n')
        
    # Create CLI module
    with open(os.path.join(pkg_dir, "cli.py"), "w") as f:
        f.write(f'''"""Command-line interface for {name}."""

def main():
    """Run the CLI application."""
    print(f"Welcome to {name}!")
    
if __name__ == "__main__":
    main()
''')
        
    if use_pyproject:
        # Create pyproject.toml
        with open(os.path.join(path, "pyproject.toml"), "w") as f:
            f.write(f'''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "A CLI application"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
readme = "README.md"
requires-python = ">=3.7"

[project.scripts]
{name} = "{name}.cli:main"
''')
    else:
        # Create setup.py
        with open(os.path.join(path, "setup.py"), "w") as f:
            f.write(f'''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    description="A CLI application",
    entry_points={{
        "console_scripts": [
            "{name}={name}.cli:main",
        ],
    }},
)
''')
    
    # Create README.md
    with open(os.path.join(path, "README.md"), "w") as f:
        f.write(f'''# {name}

A CLI application.

## Installation

```
pip install .
```

## Usage

```
{name}
```
''')