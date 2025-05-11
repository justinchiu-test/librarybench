"""
Setup script for SyncDB.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="syncdb",
    version="0.1.0",
    author="Miguel Mobile Developer",
    author_email="miguel@example.com",
    description="In-Memory Database with Mobile Synchronization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miguel/syncdb",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    extras_require={
        "test": [
            "pytest",
            "pytest-json-report",
        ],
    },
)