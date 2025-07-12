from setuptools import setup, find_packages

setup(
    name="pymockapi",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "pydantic>=2.0.0",
        "websockets>=11.0",
        "eth-utils>=2.2.0",
        "eth-hash[pycryptodome]>=0.5.0",
        "hexbytes>=0.3.0",
        "rlp>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-json-report>=1.5.0",
            "httpx>=0.24.0",
            "web3>=6.0.0",
            "ruff>=0.1.0",
            "pyright>=1.1.300",
        ]
    },
)