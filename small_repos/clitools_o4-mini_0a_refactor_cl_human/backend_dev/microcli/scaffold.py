import os

SETUP_PY = """from setuptools import setup

setup(
    name='{name}',
    version='0.1.0',
    packages=['{name}'],
    entry_points={{
        'console_scripts': [
            '{name}={name}.cli:main'
        ]
    }},
)
"""

PYPROJECT_TOML = """[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"

[project.scripts]
{name} = "{name}.cli:main"
"""

def gen_scaffold(path: str, name: str, use_pyproject: bool = False) -> None:
    os.makedirs(path, exist_ok=True)
    if use_pyproject:
        content = PYPROJECT_TOML.format(name=name)
        filename = os.path.join(path, "pyproject.toml")
    else:
        content = SETUP_PY.format(name=name)
        filename = os.path.join(path, "setup.py")
    with open(filename, "w") as f:
        f.write(content)
