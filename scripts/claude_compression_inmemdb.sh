#!/bin/bash
# Script to prepare directory structure for unified in-memory database library

set -e

# Directory containing the implementations
directory="projects/in_memory_database"

echo "Starting refactoring for $directory..."

# Create unified directory structure if it doesn't exist
if [ ! -d "$directory/unified" ]; then
    echo "Creating unified directory structure..."
    mkdir -p "$directory/unified/src"
    mkdir -p "$directory/unified/tests"

    # Initialize unified library structure
    cat > "$directory/unified/setup.py" << 'EOF'
from setuptools import setup, find_packages

setup(
    name="unified_inmemdb",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
)
EOF

    # Initialize src directory with __init__.py
    cat > "$directory/unified/src/__init__.py" << 'EOF'
# Unified In-Memory Database shared library
EOF

    # Initialize package directory
    mkdir -p "$directory/unified/src/unified_inmemdb"
    cat > "$directory/unified/src/unified_inmemdb/__init__.py" << 'EOF'
# Unified In-Memory Database package
EOF

    # Create placeholder for PLAN.md
    touch "$directory/unified/PLAN.md"

    # Create a README.md file
    cat > "$directory/unified/README.md" << 'EOF'
# Unified In-Memory Database Library

This library provides a shared implementation that can be used by both:
- VectorDB (ML Engineer)
- SyncDB (Mobile Developer)

## Installation

To install the unified library:

```bash
pip install -e .
```

## Usage

Import components from the library:

```python
from unified_inmemdb import core
```

## Documentation

See PLAN.md for the architectural design and component documentation.
EOF

    echo "Unified directory structure created."
fi

# Run Claude Code and tell it to follow instructions in REFACTOR.md
echo "Running Claude Code to implement the unified library..."
claude --dangerously-skip-permissions -p "I've created the initial structure for a unified in-memory database library at:
/home/justinchiu_cohere_com/librarybench/projects/in_memory_database/unified/

Your task is to implement this unified library following the instructions in /home/justinchiu_cohere_com/librarybench/REFACTOR.md.

Please:
1. Read the REFACTOR.md file to understand the task
2. Analyze both the ML Engineer (VectorDB) and Mobile Developer (SyncDB) implementations
3. Create a unified library in unified/src/ with common core and specialized components
4. Document your architecture in unified/PLAN.md
5. Update both implementations to import from the unified library
6. Install the unified library in both environments as needed
7. Ensure all tests from both projects pass

The unified library should provide all functionality needed by both implementations while eliminating code duplication. You should not modify any code outside the unified/ directory except for import paths. All functionality must be preserved for both use cases."

echo "Done!"
