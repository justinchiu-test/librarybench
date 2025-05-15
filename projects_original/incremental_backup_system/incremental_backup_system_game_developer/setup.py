from setuptools import setup, find_packages

setup(
    name="gamevault",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "pytest>=7.0.0",
        "pytest-json-report>=1.0.0",
        "numpy>=1.22.0",
        "xxhash>=3.0.0",  # For fast hashing
        "pyzstd>=0.15.0",  # For compression
        "bsdiff4>=1.2.0",  # For binary diffing
    ],
    python_requires=">=3.8",
    author="Mateo Game Developer",
    description="A specialized incremental backup system for game development",
)