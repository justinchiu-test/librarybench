# Lightweight Package Manager with Advanced Features

A modern package manager that handles installation, removal, and querying of software packages with dependencies. It supports semantic versioning, dependency constraint solving, virtual environments, and lockfile generation.

## Features

### Basic Features (V1)
- Install packages with their dependencies
- Remove packages (only if they are not dependencies of other packages)
- List all installed packages
- Check if a package is installed
- Circular dependency detection

### Advanced Features (V2)
- **Semantic Versioning Support**: Install packages with specific versions and version constraints
- **Dependency Constraint Solver**: Automatically resolves compatible versions of all dependencies
- **Virtual Environments**: Create and manage isolated environments for different projects
- **Lockfile Generation**: Freeze installed versions for reproducible environments
- **Package Registry**: Maintain a registry of available packages and versions
- **Search API**: Find packages matching specific version requirements
- **Why Command**: Explains why a package was installed (e.g., as a dependency of what)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd dependency_resolver

# Install dependencies
uv sync
```

## Usage

### As a Library

```python
from package_manager import PackageManager

# Create a package manager
pm = PackageManager()

# Add packages to registry
pm.add_to_registry("A", "1.0", [])
pm.add_to_registry("A", "2.0", [])
pm.add_to_registry("B", "1.0", ["A>=1.0,<2.0"])

# Create environments
pm.create_env("prod")
pm.create_env("dev")

# Use an environment
pm.use_env("dev")

# Install packages with version constraints
pm.install("B==1.0")  # Will also install A 1.0 as a dependency

# Check if a package is installed
pm.is_installed("A", "1.0")  # True
pm.is_installed("A", "2.0")  # False

# Find out why a package was installed
pm.why("A")  # "dependency of B==1.0"

# Generate a lockfile
lockfile_path = pm.generate_lockfile("dev")

# Switch environments
pm.use_env("prod")

# Install from a lockfile
pm.install_from_lockfile(lockfile_path)
```

### Command Line Interface

```bash
# Add package to registry
./cli.py registry add A 1.0 --dependencies B==1.0

# Create and use environments
./cli.py env create dev
./cli.py env use dev

# Install a package with version constraint
./cli.py install "A>=1.0"

# Generate a lockfile
./cli.py lock --environment dev --output dev.lock.json

# Install from a lockfile
./cli.py install-lockfile dev.lock.json

# List installed packages
./cli.py list

# Check if a package is installed
./cli.py check A --version 1.0

# Find packages matching a version spec
./cli.py find A --version-spec ">=1.0,<2.0"

# Explain why a package was installed
./cli.py why B
```

### Running Tests

```bash
uv run pytest tests.py
```

## Registry Format

The registry is stored in a JSON file with the following format:

```json
{
  "package_name": {
    "1.0": ["dependency1==1.0", "dependency2>=2.0"],
    "2.0": ["dependency1>=1.5"]
  },
  "dependency1": {
    "1.0": [],
    "1.5": [],
    "2.0": []
  }
}
```

## Technical Details

- Implemented in Python with static type checking
- Uses Pydantic for data models
- Supports semantic versioning with operators (`==`, `>=`, `<=`, `>`, `<`, `!=`)
- Detects circular dependencies and version conflicts
- Prevents removal of packages that are dependencies of other packages
- Supports isolated environments for different package sets
- Generates lockfiles for reproducible environments