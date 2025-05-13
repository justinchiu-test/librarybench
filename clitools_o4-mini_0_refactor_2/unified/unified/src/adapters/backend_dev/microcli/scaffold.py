"""
Project scaffolding for backend_dev microcli.
Generate setup.py or pyproject.toml.
"""
import os

def gen_scaffold(path, name, use_pyproject=False):
    """
    Generate a project scaffold at `path` with project `name`.
    If use_pyproject is True, create pyproject.toml; otherwise setup.py.
    """
    os.makedirs(path, exist_ok=True)
    if use_pyproject:
        fpath = os.path.join(path, 'pyproject.toml')
        with open(fpath, 'w') as f:
            f.write(f"[project]\nname = \"{name}\"\n")
    else:
        fpath = os.path.join(path, 'setup.py')
        with open(fpath, 'w') as f:
            f.write("from setuptools import setup\n")
            f.write(
                f"setup(name=\"{name}\",\n"
                "      entry_points={'console_scripts': []})\n"
            )