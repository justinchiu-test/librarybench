from setuptools import setup, find_packages

setup(
    name="text_editor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
)