from setuptools import setup, find_packages

setup(
    name="pypatternguard",
    version="1.0.0",
    description="Performance Pattern Detection Engine for Python codebases",
    author="Performance Engineer",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-json-report>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "pypatternguard=pypatternguard.cli:main",
        ],
    },
)