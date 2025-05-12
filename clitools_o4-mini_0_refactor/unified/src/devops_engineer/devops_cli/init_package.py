"""
Initialize Python package for devops engineers.
"""
import os

def init_package(name, use_pyproject=False, target_dir=None):
    if target_dir is None:
        target_dir = os.getcwd()
    os.makedirs(target_dir, exist_ok=True)
    if use_pyproject:
        content = f"[project]\nname = \"{name}\"\nversion = \"0.1.0\"\n"
        filename = 'pyproject.toml'
    else:
        content = f"from setuptools import setup\n\nsetup(name=\"{name}\")\n"
        filename = 'setup.py'
    path = os.path.join(target_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return content