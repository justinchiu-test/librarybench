# Unified In-Memory Database Refactoring Project

## Overview
This project requires creating a shared library for two specialized in-memory database implementations (ML Engineer's VectorDB and Mobile Developer's SyncDB) that eliminates redundancy while ensuring all requirements are met. The unified codebase must support both application domains through a common core with specialized extensions.

## Task Description
You need to create a shared, unified library in the `projects/in_memory_database/unified` directory that can be imported by both the ML Engineer implementation and Mobile Developer implementation. This library should consolidate common functionality while providing specialized components for each domain's unique requirements.

## Key Requirements

1. **Create a Unified Core Library**
   - Implement a shared in-memory database engine with common functionality
   - Design modular components that can be extended for specialized use cases
   - Place all code in the `projects/in_memory_database/unified/src/` directory
   - Ensure the library is importable by both implementations

2. **Support ML Engineer Requirements**
   - Vector data types with optimized distance calculations
   - Feature store with versioning and lineage
   - Batch prediction optimization
   - Automatic feature normalization and transformation
   - A/B testing support

3. **Support Mobile Developer Requirements**
   - Differential sync protocol
   - Conflict resolution strategies
   - Type-aware payload compression
   - Automatic schema migration
   - Battery-aware operation modes

4. **Maintain Test Compatibility**
   - Update import paths in both implementations to use the unified library
   - Ensure all tests from both implementations pass with the unified library
   - Make NO modifications to existing test files

5. **Code Organization**
   - Create a clean, modular architecture with clear separation of concerns
   - Document the design with a detailed PLAN.md file
   - Use interfaces and abstraction to support both domains
   - Eliminate code duplication through shared components

## Technical Requirements

### Implementation Rules
- **Source Code Location**: ALL source code MUST be placed in the `projects/in_memory_database/unified/src/` directory
- **Import Strategy**: The unified library must be importable by both implementations
- **NO modifications** to any code outside the `unified/` directory except for import paths
- **NO importing** code from outside the `unified/` directory

### Testability Requirements
- All tests from both original implementations must pass when using the unified library
- Tests must validate functionality from both domains
- Performance must meet or exceed the requirements of both domains

### Performance Expectations
- The unified library must maintain or improve upon the performance metrics specified in both original implementations
- No functionality should be compromised for the sake of unification
- Domain-specific optimizations must be preserved

### Key Constraints
- The implementation must use only Python standard library with no external dependencies
- All functionality must be testable without manual intervention
- The solution must satisfy all requirements from both original implementations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest.

## Core Functionality

The system must provide the following core functionality:

1. **In-Memory Database Engine**
   - Efficient in-memory data storage with schema definitions
   - Indexing mechanisms for fast retrieval
   - Standard CRUD operations with transactional integrity
   - Query capabilities for different access patterns

2. **Change Tracking and Versioning**
   - Record-level versioning and change history
   - Timestamp-based tracking for synchronization
   - Historical data access for both domains

3. **ML-Specific Extensions**
   - Vector operations and similarity search
   - Feature store with lineage tracking
   - Batch processing optimizations
   - Feature transformation framework

4. **Mobile-Specific Extensions**
   - Sync protocol for differential updates
   - Conflict resolution framework
   - Compression algorithms for efficient data transfer
   - Schema migration and compatibility management

## Testing Requirements

### Testing Methodology
- For the unified library, run tests using pytest with the specified command:
  ```
  cd projects/in_memory_database/unified/
  pytest tests/ --json-report --json-report-file=report.json --continue-on-collection-errors
  ```
- Additionally, you must run the original tests in both implementation directories to verify compatibility
- Tests must validate that both application domains function correctly with the unified library
- Performance benchmarks must be maintained for both domains

### Key Functionalities to Verify
- Proper functionality of shared core components
- Domain-specific features for ML applications
- Domain-specific features for mobile applications
- Cross-domain compatibility and integration

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of critical domain-specific functionality
- All error handling paths must be tested
- Performance tests must cover both domains' requirements

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- The report.json file must be included as proof that all tests pass

## Development Steps

### 1. Analysis Phase
- Examine both implementations to identify common functionality
- Understand domain-specific requirements for each application
- Map out shared interfaces and components

### 2. Design Phase
- Create a detailed architecture plan in `unified/PLAN.md`
- Define component boundaries and responsibilities
- Design interfaces for domain-specific extensions

### 3. Implementation Phase
- Build the core shared library components
- Implement domain-specific extensions
- Create necessary factory methods and configuration options

### 4. Integration Phase
- Update import paths in both implementations to use the unified library
- Add the unified library as a dependency in both project configurations
- Ensure all tests pass with the unified library
- Optimize for both domains' performance requirements

#### Adding the Unified Library as a Dependency

For each implementation (ML Engineer and Mobile Developer), you must add the unified library as a dependency. Here's how to do it for different project configurations:

**For setup.py projects:**
```python
from setuptools import setup, find_packages

setup(
    name="vector_db",  # or "sync_db" for mobile implementation
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Regular dependencies here
    dependency_links=[
        "../unified/"  # Relative path to unified library
    ],
)
```

**For pyproject.toml projects:**
```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

# Add local path dependency to the unified library
[tool.pip]
dependencies = [
    {path = "../unified", develop = true}
]
```

**Alternative method using pip:**
You can also install the unified library in development mode using pip:
```bash
# From the ML Engineer or Mobile Developer directory
pip install -e ../unified/
```

IMPORTANT: You must ensure the unified library is properly installed in both project environments to allow imports to function correctly.

### 5. Verification Phase
- Run all tests in both subdirectories to ensure complete functionality
- Follow the original testing instructions in each subdirectory:
  ```bash
  # For ML Engineer implementation
  cd projects/in_memory_database/in_memory_database_ml_engineer/
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json --continue-on-collection-errors
  
  # For Mobile Developer implementation
  cd projects/in_memory_database/in_memory_database_mobile_developer/
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json --continue-on-collection-errors
  ```
- Benchmark performance against original implementations
- Document the final architecture and design decisions

IMPORTANT: You must ensure that ALL tests in BOTH original implementations pass with the unified library. The original test files must not be modified; only the implementation code should import from the unified library.

## Success Criteria

The implementation will be considered successful if:

1. All tests from both original implementations pass when using the unified library
2. The unified library meets or exceeds the performance requirements of both domains
3. Code duplication is minimized through shared components
4. The architecture is clean, modular, and maintainable
5. Domain-specific functionality is preserved without compromise

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid report.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements from both original personas

## Development Setup

To set up the development environment:

1. Clone the repository and navigate to the project directory
2. Create a virtual environment using:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Install the project in development mode:
   ```
   uv pip install -e .
   ```
5. Run tests with:
   ```
   pytest tests/ --json-report --json-report-file=report.json --continue-on-collection-errors
   ```

CRITICAL REMINDER: Generating and providing the report.json file is a MANDATORY requirement for project completion.