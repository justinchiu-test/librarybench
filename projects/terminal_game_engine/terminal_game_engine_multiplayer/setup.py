from setuptools import setup, find_packages

setup(
    name="pytermgame",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-json-report>=1.5.0",
            "ruff>=0.1.0",
            "pyright>=1.1.0",
        ]
    },
)