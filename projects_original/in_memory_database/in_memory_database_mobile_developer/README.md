# SyncDB: In-Memory Database with Mobile Synchronization

A specialized in-memory database designed for mobile application backends that efficiently manages data synchronization between server and client applications with intermittent connectivity.

## Features

- **In-Memory Database Engine**: Efficient data storage with CRUD operations
- **Differential Sync Protocol**: Minimizes data transfer by only sending changes
- **Conflict Resolution**: Multiple strategies for handling concurrent changes
- **Type-Aware Compression**: Optimized data transfer size for mobile networks
- **Schema Migration**: Seamless evolution of database schema
- **Battery-Aware Operations**: Configurable performance profiles for mobile devices

## Getting Started

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Run tests
pytest --json-report --json-report-file=pytest_results.json
```

## Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

## Documentation

The SyncDB system provides a complete API for building mobile applications that need efficient data synchronization. See the documentation for details on usage and implementation.