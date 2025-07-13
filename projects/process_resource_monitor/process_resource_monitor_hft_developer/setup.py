from setuptools import setup, find_packages

setup(
    name="hft-resource-monitor",
    version="0.1.0",
    description="High-frequency trading process resource monitor with microsecond precision",
    author="HFT Developer",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-json-report>=1.5.0",
            "pytest-cov>=4.0.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)