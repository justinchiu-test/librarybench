from setuptools import setup, find_packages

setup(
    name="pymigrate",
    version="0.1.0",
    description="A data migration framework for transitioning from monolithic databases to microservices",
    author="PyMigrate Team",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "sqlalchemy>=2.0.0",
        "redis>=4.5.0",
        "psycopg2-binary>=2.9.0",
        "httpx>=0.24.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "typing-extensions>=4.5.0",
        "networkx>=3.0",
        "asyncpg>=0.27.0",
        "aiomysql>=0.1.1",
        "motor>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-json-report>=1.5.0",
            "black>=23.3.0",
            "ruff>=0.0.272",
            "pyright>=1.1.316",
        ]
    },
)