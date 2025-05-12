"""
Project scaffolding for backend developers.
"""
import os

def gen_scaffold(target_dir, project_name, use_pyproject=False):
    os.makedirs(target_dir, exist_ok=True)
    if use_pyproject:
        content = f"[project]\nname = \"{project_name}\"\nversion = \"0.1.0\"\n"
        path = os.path.join(target_dir, 'pyproject.toml')
    else:
        content = (
            "from setuptools import setup, find_packages\n\n"
            "setup(\n"
            f"    name=\"{project_name}\",\n"
            "    version=\"0.1.0\",\n"
            "    entry_points={ 'console_scripts': [] },\n"
            ")\n"
        )
        path = os.path.join(target_dir, 'setup.py')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return None