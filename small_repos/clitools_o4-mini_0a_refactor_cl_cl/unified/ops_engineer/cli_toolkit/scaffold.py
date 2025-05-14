"""
Project scaffolding for operations engineer CLI tools.
"""

from typing import Optional


def gen_scaffold(project_name: str, use_poetry: bool = False) -> str:
    """
    Generate project scaffold and return the configuration file content.
    
    Args:
        project_name (str): Name of the project.
        use_poetry (bool): Whether to use Poetry for dependency management.
        
    Returns:
        str: Generated configuration file content.
    """
    if use_poetry:
        return f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "Operations engineering tool"
authors = ["Operations <ops@example.com>"]

[tool.poetry.dependencies]
python = "^3.7"

[tool.poetry.dev-dependencies]
pytest = "^6.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''
    else:
        return f'''from setuptools import setup, find_packages

setup(
    name='{project_name}',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={{
        'console_scripts': [
            '{project_name}={project_name}.main:main',
        ],
    }},
)
'''