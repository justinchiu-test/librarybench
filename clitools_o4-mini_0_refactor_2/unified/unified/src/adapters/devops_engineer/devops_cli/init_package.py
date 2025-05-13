"""
Initialize a Python package for DevOps Engineer CLI.
"""
import os

def init_package(name, use_pyproject=False, target_dir=None):
    if target_dir is None:
        target_dir = os.getcwd()
    os.makedirs(target_dir, exist_ok=True)
    if use_pyproject:
        path = os.path.join(target_dir, 'pyproject.toml')
        content = f'name = "{name}"'
    else:
        path = os.path.join(target_dir, 'setup.py')
        content = f'setup(name="{name}")'
    with open(path, 'w') as f:
        f.write(content)
    return content