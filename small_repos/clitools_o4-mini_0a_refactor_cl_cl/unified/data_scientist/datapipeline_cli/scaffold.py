"""
Project scaffolding utilities for data scientist CLI tools.
"""

import os
from typing import Optional


def gen_scaffold(output_dir: str, project_name: str) -> str:
    """
    Generate a project scaffold for a data pipeline project.
    
    Args:
        output_dir (str): Output directory path.
        project_name (str): Name of the project.
        
    Returns:
        str: Path to the created project directory.
    """
    # Create project directory
    project_dir = os.path.join(output_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Create pyproject.toml
    pyproject_path = os.path.join(project_dir, 'pyproject.toml')
    with open(pyproject_path, 'w') as f:
        f.write(f'''[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "Data pipeline project"
authors = [
    {{name = "Data Scientist", email = "data.scientist@example.com"}}
]
requires-python = ">=3.7"
dependencies = [
    "pandas",
    "numpy",
    "scikit-learn",
]

[project.scripts]
{project_name} = "{project_name}.main:main"
''')
    
    # Create test_config.yaml
    config_path = os.path.join(project_dir, 'test_config.yaml')
    with open(config_path, 'w') as f:
        f.write(f'''# Configuration for {project_name}
project:
  name: {project_name}
  version: 0.1.0

data:
  input_path: data/input
  output_path: data/output

pipeline:
  steps:
    - name: load_data
      enabled: true
    - name: preprocess
      enabled: true
    - name: train_model
      enabled: true
    - name: evaluate
      enabled: true
''')
    
    # Create data directories
    os.makedirs(os.path.join(project_dir, 'data', 'input'), exist_ok=True)
    os.makedirs(os.path.join(project_dir, 'data', 'output'), exist_ok=True)
    
    # Create src directory
    src_dir = os.path.join(project_dir, 'src', project_name)
    os.makedirs(src_dir, exist_ok=True)
    
    # Create __init__.py
    with open(os.path.join(src_dir, '__init__.py'), 'w') as f:
        f.write(f'"""Data pipeline package: {project_name}."""\n\n__version__ = "0.1.0"\n')
    
    # Create main.py
    with open(os.path.join(src_dir, 'main.py'), 'w') as f:
        f.write(f'''"""Main entry point for {project_name}."""

def main():
    """Run the data pipeline."""
    print("Running the data pipeline...")
    
if __name__ == "__main__":
    main()
''')
    
    return project_dir