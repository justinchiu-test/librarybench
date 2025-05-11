from setuptools import setup, find_packages

setup(
    name="securetask",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
        "pydantic>=2.0.0",
        "pycryptodome>=3.18.0",
        "python-jose>=3.3.0",
        "jinja2>=3.0.0",
        "pytest>=7.0.0",
        "pytest-benchmark>=4.0.0",
        "pytest-json-report>=1.5.0",
    ],
    python_requires=">=3.9",
)