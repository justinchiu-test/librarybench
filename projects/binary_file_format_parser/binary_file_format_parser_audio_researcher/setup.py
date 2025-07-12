from setuptools import setup, find_packages

setup(
    name="pybinparser",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-json-report>=1.5.0",
            "ruff>=0.1.0",
            "pyright>=1.1.0",
        ]
    },
)