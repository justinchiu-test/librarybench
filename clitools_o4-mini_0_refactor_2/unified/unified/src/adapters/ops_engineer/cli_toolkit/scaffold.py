"""
Project scaffolding for Operations Engineer CLI.
"""
def gen_scaffold(name, use_poetry=False):
    if use_poetry:
        return f"[tool.poetry]\nname = \"{name}\"\n"
    else:
        return f"from setuptools import setup\nsetup(name='{name}')"