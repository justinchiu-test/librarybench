"""
Project scaffolding for Data Pipeline CLI.
"""
import os
import shutil
from typing import Dict, List, Optional

class Scaffold:
    """
    Generates project scaffolds for data pipelines.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize a new scaffold generator.
        
        Args:
            templates_dir: Directory containing templates
        """
        self.templates_dir = templates_dir
    
    def create_project(self, 
                     project_dir: str,
                     project_name: str,
                     template: str = "basic",
                     variables: Optional[Dict[str, str]] = None) -> bool:
        """
        Create a new project from a template.
        
        Args:
            project_dir: Directory to create project in
            project_name: Name of the project
            template: Template to use
            variables: Template variables
            
        Returns:
            True if project was created successfully
        """
        # Create project directory
        project_path = os.path.join(project_dir, project_name)
        try:
            os.makedirs(project_path, exist_ok=True)
        except OSError:
            return False
        
        # Process template variables
        vars_dict = variables or {}
        vars_dict["project_name"] = project_name
        
        # If templates_dir is provided, copy from there
        if self.templates_dir and os.path.isdir(os.path.join(self.templates_dir, template)):
            return self._copy_template(
                os.path.join(self.templates_dir, template),
                project_path,
                vars_dict
            )
        
        # Otherwise, generate files directly
        return self._generate_template(template, project_path, vars_dict)
    
    def list_templates(self) -> List[str]:
        """
        List available templates.
        
        Returns:
            List of template names
        """
        if self.templates_dir and os.path.isdir(self.templates_dir):
            # Return directories in templates_dir
            return [d for d in os.listdir(self.templates_dir) 
                  if os.path.isdir(os.path.join(self.templates_dir, d))]
        
        # Return built-in templates
        return ["basic", "complete", "minimal"]
    
    def _copy_template(self, 
                      template_dir: str, 
                      project_dir: str, 
                      variables: Dict[str, str]) -> bool:
        """
        Copy a template directory to the project directory.
        
        Args:
            template_dir: Template directory
            project_dir: Project directory
            variables: Template variables
            
        Returns:
            True if copy was successful
        """
        try:
            # Walk template directory and copy files
            for root, dirs, files in os.walk(template_dir):
                # Calculate relative path
                rel_path = os.path.relpath(root, template_dir)
                target_dir = os.path.join(project_dir, rel_path)
                
                # Create target directory
                if rel_path != '.':
                    os.makedirs(target_dir, exist_ok=True)
                
                # Copy and process files
                for file in files:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(target_dir, file)
                    
                    # Process template file
                    self._process_template_file(src_path, dst_path, variables)
            
            return True
        except OSError:
            return False
    
    def _generate_template(self, 
                         template: str, 
                         project_dir: str, 
                         variables: Dict[str, str]) -> bool:
        """
        Generate files for a template directly.
        
        Args:
            template: Template name
            project_dir: Project directory
            variables: Template variables
            
        Returns:
            True if generation was successful
        """
        project_name = variables.get("project_name", "data_pipeline")
        
        try:
            if template == "basic" or template == "complete":
                # Create package directory
                pkg_dir = os.path.join(project_dir, project_name)
                os.makedirs(pkg_dir, exist_ok=True)
                
                # Create __init__.py
                with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
                    f.write(f'"""Data pipeline package."""\n\n__version__ = "0.1.0"\n')
                
                # Create pipeline module
                with open(os.path.join(pkg_dir, "pipeline.py"), "w") as f:
                    f.write(f'''"""Data pipeline implementation."""

def run_pipeline(config_file=None):
    """
    Run the data pipeline.
    
    Args:
        config_file: Path to configuration file
    """
    print(f"Running {project_name} pipeline")
    
if __name__ == "__main__":
    run_pipeline()
''')
                
                # Create setup.py
                with open(os.path.join(project_dir, "setup.py"), "w") as f:
                    f.write(f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(),
    description="Data pipeline",
    entry_points={{
        'console_scripts': [
            '{project_name}={project_name}.pipeline:run_pipeline',
        ],
    }},
)
''')
                
                # Create README.md
                with open(os.path.join(project_dir, "README.md"), "w") as f:
                    f.write(f'''# {project_name}

A data pipeline project.

## Installation

```
pip install -e .
```

## Usage

```
{project_name} --config config.json
```
''')
                
                # Only add these files for the complete template
                if template == "complete":
                    # Create tests directory
                    tests_dir = os.path.join(project_dir, "tests")
                    os.makedirs(tests_dir, exist_ok=True)
                    
                    # Create test file
                    with open(os.path.join(tests_dir, "test_pipeline.py"), "w") as f:
                        f.write(f'''"""Tests for the data pipeline."""
import unittest
from {project_name}.pipeline import run_pipeline

class TestPipeline(unittest.TestCase):
    def test_run_pipeline(self):
        """Test that the pipeline runs without errors."""
        result = run_pipeline()
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
''')
                    
                    # Create config directory
                    config_dir = os.path.join(project_dir, "config")
                    os.makedirs(config_dir, exist_ok=True)
                    
                    # Create config file
                    with open(os.path.join(config_dir, "config.json"), "w") as f:
                        f.write('''{
    "input_file": "data/input.csv",
    "output_file": "data/output.csv",
    "log_level": "INFO",
    "batch_size": 1000
}
''')
                    
                    # Create data directory
                    data_dir = os.path.join(project_dir, "data")
                    os.makedirs(data_dir, exist_ok=True)
                    
                    # Create gitignore
                    with open(os.path.join(project_dir, ".gitignore"), "w") as f:
                        f.write('''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Data files
data/*.csv
data/*.json
''')
            
            elif template == "minimal":
                # Create a single file with a main function
                with open(os.path.join(project_dir, f"{project_name}.py"), "w") as f:
                    f.write(f'''"""Minimal data pipeline implementation."""

def main():
    """Run the data pipeline."""
    print("Running minimal data pipeline")

if __name__ == "__main__":
    main()
''')
                
                # Create README.md
                with open(os.path.join(project_dir, "README.md"), "w") as f:
                    f.write(f'''# {project_name}

A minimal data pipeline.

## Usage

```
python {project_name}.py
```
''')
            
            else:
                # Unknown template
                return False
            
            return True
        except OSError:
            return False
    
    def _process_template_file(self, 
                              src_path: str, 
                              dst_path: str, 
                              variables: Dict[str, str]) -> None:
        """
        Process a template file by replacing variables.
        
        Args:
            src_path: Source file path
            dst_path: Destination file path
            variables: Template variables
        """
        # Skip binary files
        binary_extensions = ['.pyc', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar.gz']
        if any(src_path.endswith(ext) for ext in binary_extensions):
            shutil.copy2(src_path, dst_path)
            return
        
        # Read source file
        with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace variables
        for key, value in variables.items():
            content = content.replace(f"{{{{{{ {key} }}}}}}", value)
        
        # Write processed content
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Create a global scaffold instance
_scaffold = Scaffold()

def create_project(project_dir: str,
                 project_name: str,
                 template: str = "basic",
                 variables: Optional[Dict[str, str]] = None) -> bool:
    """
    Create a new project from a template.
    
    Args:
        project_dir: Directory to create project in
        project_name: Name of the project
        template: Template to use
        variables: Template variables
        
    Returns:
        True if project was created successfully
    """
    return _scaffold.create_project(project_dir, project_name, template, variables)

def list_templates() -> List[str]:
    """
    List available templates.
    
    Returns:
        List of template names
    """
    return _scaffold.list_templates()


def gen_scaffold(output_dir: str, project_name: str) -> str:
    """
    Generate a scaffold for a data science project.
    
    Args:
        output_dir: Directory to create project in
        project_name: Name of the project
        
    Returns:
        Path to generated project
    """
    # Create project directory
    project_path = os.path.join(output_dir, project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # Create pyproject.toml
    with open(os.path.join(project_path, 'pyproject.toml'), 'w') as f:
        f.write(f'''[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "Data science project"
authors = ["Data Scientist <data@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
pandas = "^1.3.0"
numpy = "^1.21.0"
scikit-learn = "^1.0.0"
matplotlib = "^3.4.0"
jupyter = "^1.0.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.5"
black = "^21.9b0"
flake8 = "^4.0.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
''')
    
    # Create README.md
    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write(f'''# {project_name}

A data science project.

## Setup

```bash
poetry install
```

## Usage

```bash
poetry run jupyter notebook
```
''')
    
    # Create test_config.yaml
    with open(os.path.join(project_path, 'test_config.yaml'), 'w') as f:
        f.write('''# Data pipeline configuration
input:
  file: data/input.csv
  format: csv
  has_header: true

output:
  file: data/output.csv
  format: csv
  include_header: true

processing:
  batch_size: 1000
  num_workers: 4
  log_level: INFO
''')
    
    # Create folders
    os.makedirs(os.path.join(project_path, 'data'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'notebooks'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)
    
    # Create src/__init__.py
    with open(os.path.join(project_path, 'src', '__init__.py'), 'w') as f:
        f.write('')
    
    # Create src/pipeline.py
    with open(os.path.join(project_path, 'src', 'pipeline.py'), 'w') as f:
        f.write('''"""
Data processing pipeline.
"""

import yaml
import pandas as pd


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_pipeline(config_path):
    """Run the data processing pipeline."""
    # Load configuration
    config = load_config(config_path)
    
    # Load input data
    input_file = config['input']['file']
    df = pd.read_csv(input_file)
    
    # Process data (example)
    # ... add your processing steps here ...
    
    # Save output
    output_file = config['output']['file']
    df.to_csv(output_file, index=False)
    
    return df
''')
    
    # Create notebook
    with open(os.path.join(project_path, 'notebooks', 'exploration.ipynb'), 'w') as f:
        f.write('''{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Data Exploration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import pandas as pd\\n",
    "import matplotlib.pyplot as plt\\n",
    "import numpy as np\\n",
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Load data\\n",
    "# df = pd.read_csv('../data/input.csv')\\n",
    "# df.head()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
''')
    
    return project_path