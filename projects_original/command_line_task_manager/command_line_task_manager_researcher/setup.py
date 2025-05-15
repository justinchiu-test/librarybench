from setuptools import setup, find_packages

setup(
    name="researchtrack",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pybtex>=0.24.0",
        "packaging>=23.0",
        "markdown>=3.4.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-json-report>=1.5.0",
            "black>=23.0.0",
            "ruff>=0.0.0",
            "pyright>=0.0.0",
        ],
    },
    python_requires=">=3.8",
    description="A specialized command-line task management system for academic research",
    author="Dr. Patel",
    author_email="researcher@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)