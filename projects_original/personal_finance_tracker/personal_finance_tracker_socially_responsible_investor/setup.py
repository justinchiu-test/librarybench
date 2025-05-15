from setuptools import setup, find_packages

setup(
    name="ethical_finance",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "pytest>=7.0.0",
        "pytest-json-report>=1.5.0",
    ],
    python_requires=">=3.9",
)