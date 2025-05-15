from setuptools import setup, find_packages

setup(
    name="file_system_analyzer_db_admin",
    version="0.1.0",
    description="Database Storage Optimization Analyzer",
    author="Elena DB Admin",
    author_email="elena@dbadmin.example.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-benchmark>=3.4.0",
            "pytest-json-report>=1.5.0",
        ],
    },
    python_requires=">=3.8",
)