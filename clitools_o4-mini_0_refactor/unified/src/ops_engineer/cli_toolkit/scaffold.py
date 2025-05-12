"""
Project scaffolding for ops engineers.
"""
def gen_scaffold(project_name, use_poetry=False):
    if use_poetry:
        # Poetry pyproject stub
        return f"[tool.poetry]\nname = \"{project_name}\"\nversion = \"0.1.0\"\n"
    # setuptools setup stub
    return f"from setuptools import setup\n\nsetup(name='{project_name}')\n"