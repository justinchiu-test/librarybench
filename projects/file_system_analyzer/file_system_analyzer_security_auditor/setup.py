from setuptools import setup, find_packages

setup(
    name="file_system_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "cryptography>=40.0.0", 
        "xxhash>=3.0.0",
        "python-magic>=0.4.24",
        "pytz",
    ],
    python_requires=">=3.8",
)