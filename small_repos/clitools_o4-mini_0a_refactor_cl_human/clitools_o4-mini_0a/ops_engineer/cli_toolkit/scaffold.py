def gen_scaffold(project_name, use_poetry=False):
    """
    Generate setup.py or pyproject.toml scaffolding for a new project.
    """
    if use_poetry:
        content = (
            "[tool.poetry]\n"
            f"name = \"{project_name}\"\n"
            "version = \"0.1.0\"\n"
        )
        return content
    else:
        content = (
            "from setuptools import setup\n\n"
            "setup(\n"
            f"    name='{project_name}',\n"
            "    version='0.1.0',\n"
            "    packages=[]\n"
            ")\n"
        )
        return content
