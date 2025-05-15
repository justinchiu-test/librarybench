"""
Project scaffolding for the CLI Toolkit.
"""
from typing import Dict, List, Optional, Union


def gen_scaffold(project_name: str, use_poetry: bool = False) -> str:
    """
    Generate project scaffold code.
    
    Args:
        project_name: Name of the project
        use_poetry: Whether to use Poetry for dependency management
        
    Returns:
        Generated scaffold code as string
    """
    if use_poetry:
        return _gen_poetry_scaffold(project_name)
    else:
        return _gen_setuppy_scaffold(project_name)


def _gen_setuppy_scaffold(project_name: str) -> str:
    """
    Generate setup.py scaffold.
    
    Args:
        project_name: Name of the project
        
    Returns:
        setup.py content
    """
    return f'''
from setuptools import setup, find_packages

setup(
    name='{project_name}',
    version='0.1.0',
    description='A CLI tool',
    author='',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'click>=7.0',
    ],
    entry_points={{
        'console_scripts': [
            '{project_name}={project_name}.cli:main',
        ],
    }},
)
'''


def _gen_poetry_scaffold(project_name: str) -> str:
    """
    Generate pyproject.toml scaffold for Poetry.
    
    Args:
        project_name: Name of the project
        
    Returns:
        pyproject.toml content
    """
    return f'''
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "A CLI tool"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
click = "^8.0.0"

[tool.poetry.dev-dependencies]
pytest = "^6.0.0"
black = "^21.5b2"
flake8 = "^3.9.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
{project_name} = "{project_name}.cli:main"
'''