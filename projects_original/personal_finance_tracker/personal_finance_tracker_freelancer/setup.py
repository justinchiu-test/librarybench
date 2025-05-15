from setuptools import setup, find_packages

setup(
    name="personal_finance_tracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "pydantic",
        "python-dateutil",
    ],
    python_requires=">=3.8",
)
