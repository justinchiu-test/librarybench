"""
Project scaffolding for backend developer CLI tools.
"""

import os

def gen_scaffold(path, name, use_pyproject=False):
    """
    Generate a Python project scaffold.
    
    Args:
        path (str): Directory to create the project in.
        name (str): Project name.
        use_pyproject (bool): Whether to use pyproject.toml instead of setup.py.
    """
    # Create project directory if it doesn't exist
    os.makedirs(path, exist_ok=True)
    
    # Create src directory
    src_dir = os.path.join(path, "src")
    os.makedirs(src_dir, exist_ok=True)
    
    # Create package directory
    pkg_dir = os.path.join(src_dir, name)
    os.makedirs(pkg_dir, exist_ok=True)
    
    # Create __init__.py
    init_path = os.path.join(pkg_dir, "__init__.py")
    with open(init_path, "w") as f:
        f.write(f'"""Package {name}."""\n\n__version__ = "0.1.0"\n')
    
    # Create main.py
    main_path = os.path.join(pkg_dir, "main.py")
    with open(main_path, "w") as f:
        f.write(f'''"""Main entry point for {name}."""

def main():
    """Run the main program."""
    print("Hello from {name}!")

if __name__ == "__main__":
    main()
''')
    
    # Create README.md
    readme_path = os.path.join(path, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"# {name}\n\nA Python project.\n")
    
    if use_pyproject:
        # Create pyproject.toml
        pyproject_path = os.path.join(path, "pyproject.toml")
        with open(pyproject_path, "w") as f:
            f.write(f'''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "A Python project"
authors = [
    {{name = "Author", email = "author@example.com"}}
]
requires-python = ">=3.7"

[project.scripts]
{name} = "{name}.main:main"
''')
    else:
        # Create setup.py
        setup_path = os.path.join(path, "setup.py")
        with open(setup_path, "w") as f:
            f.write(f'''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    entry_points={{
        "console_scripts": [
            "{name}={name}.main:main",
        ],
    }},
)
''')