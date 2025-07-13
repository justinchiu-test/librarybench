from setuptools import setup, find_packages

setup(
    name="film-archive-manager",
    version="1.0.0",
    description="Film Production Archive System for managing raw footage, VFX, and project files",
    author="Film Archive Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "pytest>=7.0.0",
        "pytest-json-report>=1.5.0",
        "aiofiles>=23.0.0",
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)