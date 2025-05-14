import os

SETUP_PY_TEMPLATE = """from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)
"""

PYPROJECT_TOML_TEMPLATE = """[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
dependencies = []
"""

def init_package(name, use_pyproject=False, target_dir="."):
    if use_pyproject:
        content = PYPROJECT_TOML_TEMPLATE.format(name=name)
        path = os.path.join(target_dir, "pyproject.toml")
    else:
        content = SETUP_PY_TEMPLATE.format(name=name)
        path = os.path.join(target_dir, "setup.py")
    with open(path, "w") as f:
        f.write(content)
    return content
