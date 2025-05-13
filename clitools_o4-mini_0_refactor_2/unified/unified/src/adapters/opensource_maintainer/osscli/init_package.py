"""
Initialize project scaffold for Open Source Maintainer CLI.
"""
import os

def init_package(path):
    # Create project directory and essential files
    os.makedirs(path, exist_ok=True)
    # setup.py
    with open(os.path.join(path, 'setup.py'), 'w') as f:
        f.write('from setuptools import setup\n')
    # GitHub Actions workflow
    workflows = os.path.join(path, '.github', 'workflows')
    os.makedirs(workflows, exist_ok=True)
    ci = os.path.join(workflows, 'ci.yml')
    with open(ci, 'w') as f:
        f.write('')
    # tests package
    tests_dir = os.path.join(path, 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    with open(os.path.join(tests_dir, '__init__.py'), 'w') as f:
        f.write('')
    return True