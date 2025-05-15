from setuptools import setup, find_packages

setup(
    name="legal_discovery_interpreter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "nltk>=3.8.1",
        "pytest>=7.0.0",
        "pytest-json-report>=1.5.0",
    ],
    python_requires=">=3.8",
)