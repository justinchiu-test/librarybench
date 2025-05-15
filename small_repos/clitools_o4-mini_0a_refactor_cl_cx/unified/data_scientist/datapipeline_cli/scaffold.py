import os
import shutil

def gen_scaffold(output_dir, project_name, use_pyproject=False):
    """
    Generate a project scaffold for data science projects
    
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
    
    # Create data directory
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "processed"), exist_ok=True)
    
    # Create notebooks directory
    notebooks_dir = os.path.join(output_dir, "notebooks")
    os.makedirs(notebooks_dir, exist_ok=True)
    
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
        f.write(f"# {project_name}\n\nA data science project.\n")
    
    if use_pyproject:
        # Create pyproject.toml
        with open(os.path.join(output_dir, "pyproject.toml"), "w") as f:
            f.write(f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A data science project"
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
    
    # Create a basic pipeline module
    with open(os.path.join(package_dir, "pipeline.py"), "w") as f:
        f.write("""import pandas as pd

def extract(source=None):
    '''Extract data from source'''
    return pd.DataFrame()
    
def transform(data, config=None):
    '''Transform the data'''
    return data
    
def load(data, target=None):
    '''Load data to target'''
    if target:
        data.to_csv(target, index=False)
    return True
""")