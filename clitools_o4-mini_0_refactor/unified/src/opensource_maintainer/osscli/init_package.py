"""
Initialize open-source project structure.
"""
import os

def init_package(path):
    # create base directory
    os.makedirs(path, exist_ok=True)
    # setup.py
    with open(os.path.join(path, 'setup.py'), 'w', encoding='utf-8') as f:
        f.write('# setup script')
    # GitHub Actions workflow
    ci_dir = os.path.join(path, '.github', 'workflows')
    os.makedirs(ci_dir, exist_ok=True)
    with open(os.path.join(ci_dir, 'ci.yml'), 'w', encoding='utf-8') as f:
        f.write('# CI configuration')
    # tests package
    tests_dir = os.path.join(path, 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    with open(os.path.join(tests_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write('# test package')
    return True