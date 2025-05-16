from setuptools import setup, find_packages

setup(
    name="unified-command_line_task_manager",
    version="0.1.0",
    description="Unified libraries for command_line_task_manager with original package names preserved",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pybtex>=0.24.0",
        "cryptography>=40.0.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tasks=cli.main:main",
        ],
    },
)
