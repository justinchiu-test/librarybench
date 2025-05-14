"""
Project scaffolding module for CLI tools.
Generates project templates and boilerplate code.
"""

import os
import re
import shutil
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional


class ScaffoldTemplate:
    """Represents a scaffolding template."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new template.
        
        Args:
            name: Name of the template
            description: Description of the template
        """
        self.name = name
        self.description = description
        self.files: Dict[str, str] = {}
        self.directories: List[str] = []
    
    def add_file(self, path: str, content: str) -> None:
        """
        Add a file template.
        
        Args:
            path: Relative path of the file within the project
            content: Content template with $VAR placeholders
        """
        self.files[path] = content
    
    def add_directory(self, path: str) -> None:
        """
        Add a directory to create.
        
        Args:
            path: Relative path of the directory within the project
        """
        self.directories.append(path)


class Scaffolder:
    """
    Project scaffolding tool.
    Generates project structure from templates.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize a new scaffolder.
        
        Args:
            template_dir: Directory containing template files
        """
        self.templates: Dict[str, ScaffoldTemplate] = {}
        self.template_dir = template_dir
        
        # If template_dir provided, load templates from there
        if template_dir and os.path.exists(template_dir):
            self._load_templates_from_dir(template_dir)
        
        # Add built-in templates
        self._add_builtin_templates()
    
    def add_template(self, template: ScaffoldTemplate) -> None:
        """
        Add a template to the scaffolder.
        
        Args:
            template: Template to add
        """
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[ScaffoldTemplate]:
        """
        Get a template by name.
        
        Args:
            name: Name of the template
            
        Returns:
            Template or None if not found
        """
        return self.templates.get(name)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List available templates.
        
        Returns:
            List of template info dictionaries
        """
        return [
            {"name": name, "description": template.description}
            for name, template in self.templates.items()
        ]
    
    def generate(self, 
                template_name: str, 
                output_dir: str, 
                variables: Dict[str, Any] = None) -> bool:
        """
        Generate a project from a template.
        
        Args:
            template_name: Name of the template to use
            output_dir: Directory to generate the project in
            variables: Variables to substitute in templates
            
        Returns:
            True if generation succeeded, False otherwise
        """
        template = self.get_template(template_name)
        if not template:
            return False
        
        variables = variables or {}
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create directories
            for dir_path in template.directories:
                path = os.path.join(output_dir, self._substitute_path(dir_path, variables))
                os.makedirs(path, exist_ok=True)
            
            # Create files
            for file_path, content in template.files.items():
                # Substitute path variables
                path = os.path.join(output_dir, self._substitute_path(file_path, variables))
                
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(path), exist_ok=True)
                
                # Substitute content variables
                tmpl = Template(content)
                final_content = tmpl.safe_substitute(variables)
                
                # Write file
                with open(path, 'w') as f:
                    f.write(final_content)
            
            return True
            
        except Exception:
            return False
    
    def _substitute_path(self, path: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in a path."""
        for key, value in variables.items():
            var_pattern = f"${key}"
            path = path.replace(var_pattern, str(value))
        return path
    
    def _load_templates_from_dir(self, template_dir: str) -> None:
        """
        Load templates from a directory.
        
        Args:
            template_dir: Directory containing template files
        """
        for item in os.listdir(template_dir):
            item_path = os.path.join(template_dir, item)
            if os.path.isdir(item_path):
                self._load_template_from_subdir(item, item_path)
    
    def _load_template_from_subdir(self, name: str, dir_path: str) -> None:
        """
        Load a template from a subdirectory.
        
        Args:
            name: Name of the template (directory name)
            dir_path: Path to the template directory
        """
        # Check if directory contains a metadata file
        meta_path = os.path.join(dir_path, 'template.meta')
        description = ""
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('description='):
                        description = line[12:].strip('"\'')
        
        # Create template
        template = ScaffoldTemplate(name, description)
        
        # Find the content directory
        content_dir = os.path.join(dir_path, 'content')
        if not os.path.exists(content_dir):
            content_dir = dir_path
        
        # Add files and directories
        for root, dirs, files in os.walk(content_dir):
            # Get relative path from content directory
            rel_path = os.path.relpath(root, content_dir)
            if rel_path != '.':
                template.add_directory(rel_path)
            
            # Add files
            for file in files:
                if file == 'template.meta':
                    continue
                
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file)
                if rel_file_path.startswith('./'):
                    rel_file_path = rel_file_path[2:]
                
                with open(file_path, 'r') as f:
                    try:
                        content = f.read()
                        template.add_file(rel_file_path, content)
                    except UnicodeDecodeError:
                        # Skip binary files
                        pass
        
        # Add template to collection
        self.templates[name] = template
    
    def _add_builtin_templates(self) -> None:
        """Add built-in templates."""
        # Python package template
        py_pkg = ScaffoldTemplate("python-package", "Basic Python package structure")
        
        py_pkg.add_directory("$package_name")
        py_pkg.add_directory("tests")
        py_pkg.add_directory("docs")
        
        py_pkg.add_file("$package_name/__init__.py", """\"\"\"
$package_name package.
$package_description
\"\"\"

__version__ = "$version"
""")
        
        py_pkg.add_file("setup.py", """from setuptools import setup, find_packages

setup(
    name="$package_name",
    version="$version",
    packages=find_packages(),
    description="$package_description",
    author="$author",
    author_email="$author_email",
    url="$url",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
""")
        
        py_pkg.add_file("README.md", """# $package_name

$package_description

## Installation

```
pip install $package_name
```

## Usage

```python
import $package_name

# Add usage examples here
```

## License

$license
""")
        
        py_pkg.add_file("tests/__init__.py", "")
        py_pkg.add_file("tests/test_basic.py", """import unittest
import $package_name

class TestBasic(unittest.TestCase):
    def test_import(self):
        self.assertIsNotNone($package_name.__version__)

if __name__ == "__main__":
    unittest.main()
""")
        
        self.templates["python-package"] = py_pkg
        
        # CLI tool template
        cli_tool = ScaffoldTemplate("cli-tool", "Command line tool structure")
        
        cli_tool.add_directory("$package_name")
        cli_tool.add_directory("$package_name/commands")
        cli_tool.add_directory("tests")
        
        cli_tool.add_file("$package_name/__init__.py", """\"\"\"
$package_name CLI tool.
$package_description
\"\"\"

__version__ = "$version"
""")
        
        cli_tool.add_file("$package_name/__main__.py", """\"\"\"
Entry point for $package_name CLI.
\"\"\"

from .cli import main

if __name__ == "__main__":
    main()
""")
        
        cli_tool.add_file("$package_name/cli.py", """\"\"\"
CLI entry point for $package_name.
\"\"\"

import argparse
import sys
from . import __version__
from .commands import get_commands

def main():
    parser = argparse.ArgumentParser(description="$package_description")
    parser.add_argument("--version", action="version", version=f"$package_name {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Register commands
    commands = get_commands()
    for name, cmd in commands.items():
        cmd_parser = subparsers.add_parser(name, help=cmd.description)
        cmd.register_arguments(cmd_parser)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    cmd = commands[args.command]
    return cmd.execute(args)

if __name__ == "__main__":
    sys.exit(main())
""")
        
        cli_tool.add_file("$package_name/commands/__init__.py", """\"\"\"
Command registry for $package_name.
\"\"\"

from typing import Dict, Type
from .base import Command
from .hello import HelloCommand

def get_commands() -> Dict[str, Command]:
    \"\"\"
    Get all available commands.
    
    Returns:
        Dictionary of command name to command instance
    \"\"\"
    return {
        "hello": HelloCommand(),
        # Add more commands here
    }
""")
        
        cli_tool.add_file("$package_name/commands/base.py", """\"\"\"
Base command class for $package_name.
\"\"\"

import argparse
from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    \"\"\"Base command class.\"\"\"
    
    @property
    def name(self) -> str:
        \"\"\"Name of the command.\"\"\"
        return self.__class__.__name__.lower().replace("command", "")
    
    @property
    def description(self) -> str:
        \"\"\"Description of the command.\"\"\"
        return self.__doc__ or "No description"
    
    @abstractmethod
    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        \"\"\"Register command-specific arguments.\"\"\"
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        \"\"\"Execute the command.\"\"\"
        pass
""")
        
        cli_tool.add_file("$package_name/commands/hello.py", """\"\"\"
Hello world command for $package_name.
\"\"\"

import argparse
from .base import Command

class HelloCommand(Command):
    \"\"\"Print a hello message.\"\"\"
    
    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--name", default="World", help="Name to greet")
    
    def execute(self, args: argparse.Namespace) -> int:
        print(f"Hello, {args.name}!")
        return 0
""")
        
        cli_tool.add_file("setup.py", """from setuptools import setup, find_packages

setup(
    name="$package_name",
    version="$version",
    packages=find_packages(),
    description="$package_description",
    author="$author",
    author_email="$author_email",
    url="$url",
    entry_points={
        "console_scripts": [
            "$package_name=$package_name.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
""")
        
        cli_tool.add_file("README.md", """# $package_name

$package_description

## Installation

```
pip install $package_name
```

## Usage

```
$package_name --help
$package_name hello --name YourName
```

## License

$license
""")
        
        cli_tool.add_file("tests/__init__.py", "")
        cli_tool.add_file("tests/test_hello.py", """import unittest
from unittest.mock import patch
import io
import sys
from $package_name.commands.hello import HelloCommand

class TestHelloCommand(unittest.TestCase):
    def test_execute(self):
        cmd = HelloCommand()
        args = type("Args", (), {"name": "Test"})()
        
        # Capture stdout
        captured_output = io.StringIO()
        with patch("sys.stdout", new=captured_output):
            result = cmd.execute(args)
        
        self.assertEqual(result, 0)
        self.assertEqual(captured_output.getvalue().strip(), "Hello, Test!")

if __name__ == "__main__":
    unittest.main()
""")
        
        self.templates["cli-tool"] = cli_tool


# Create a global scaffolder for convenience
_global_scaffolder = Scaffolder()

def add_template(template: ScaffoldTemplate) -> None:
    """Add a template to the global scaffolder."""
    _global_scaffolder.add_template(template)

def get_template(name: str) -> Optional[ScaffoldTemplate]:
    """Get a template from the global scaffolder."""
    return _global_scaffolder.get_template(name)

def list_templates() -> List[Dict[str, str]]:
    """List templates from the global scaffolder."""
    return _global_scaffolder.list_templates()

def generate(template_name: str, output_dir: str, variables: Dict[str, Any] = None) -> bool:
    """Generate a project using the global scaffolder."""
    return _global_scaffolder.generate(template_name, output_dir, variables)

def configure(template_dir: Optional[str] = None) -> None:
    """Configure the global scaffolder."""
    global _global_scaffolder
    _global_scaffolder = Scaffolder(template_dir)