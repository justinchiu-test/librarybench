from setuptools import setup, find_packages

setup(
    name="privacy_query_interpreter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "cryptography>=40.0.0",
        "regex>=2022.0.0",
        "pandas>=2.0.0",
        "sqlparse>=0.4.4",
        "pytest>=7.0.0",
        "pytest-json-report>=1.5.0",
    ],
    python_requires=">=3.8",
    description="Privacy-Focused Query Language Interpreter for data privacy officers",
)