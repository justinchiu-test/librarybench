from setuptools import setup, find_packages

setup(
    name="pypatternguard",
    version="1.0.0",
    description="Security vulnerability detection engine for fintech applications",
    author="Security Auditor",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-json-report>=1.5.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)