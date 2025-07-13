from setuptools import setup, find_packages

setup(
    name="pytermgame",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pydantic>=2.0.0",
        "colorama>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-json-report>=1.5.0",
            "black>=22.0.0",
            "mypy>=0.900",
        ]
    },
    python_requires=">=3.8",
    author="PyTermGame Team",
    description="A terminal-based game engine focused on creating visually stunning games using advanced ASCII art rendering techniques",
    long_description_content_type="text/markdown",
)