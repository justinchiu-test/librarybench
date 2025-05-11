"""Setup script for ResearchBrain package."""

from setuptools import setup, find_packages

setup(
    name="researchbrain",
    version="0.1.0",
    description="A personal knowledge management system for academic researchers",
    author="Academic Researcher",
    author_email="researcher@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.5.0",
        "pypdf>=3.17.0",
        "bibtexparser>=1.4.0",
        "pybtex>=0.24.0",
        "markdown>=3.5.1",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "rich>=13.6.0",
        "tqdm>=4.66.1",
        "pyarrow>=14.0.0",
        "pandas>=2.1.2",
        "networkx>=3.2.1",
        "python-multipart>=0.0.6",
        "pyyaml>=6.0.1",
        "jinja2>=3.1.2",
    ],
    entry_points={
        'console_scripts': [
            'researchbrain=researchbrain.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.10",
)