import os

def init_package(path):
    os.makedirs(path, exist_ok=True)
    setup_py = os.path.join(path, "setup.py")
    with open(setup_py, "w") as f:
        f.write("from setuptools import setup\n\nsetup()\n")
    workflows = os.path.join(path, ".github", "workflows")
    os.makedirs(workflows, exist_ok=True)
    ci_file = os.path.join(workflows, "ci.yml")
    with open(ci_file, "w") as f:
        f.write("name: CI\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n")
    tests_dir = os.path.join(path, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    open(os.path.join(path, "__init__.py"), "w").close()
    open(os.path.join(tests_dir, "__init__.py"), "w").close()
    return True
