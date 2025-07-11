# Build Pipeline Dependency Optimizer

## Overview
A build-focused dependency analysis tool that helps DevOps specialists optimize compilation times and build pipelines by understanding module dependencies, enabling parallel builds, and implementing intelligent caching strategies.

## Persona Description
A DevOps specialist optimizing build pipelines and compilation times for large projects. They need to understand dependency graphs to parallelize builds effectively.

## Key Requirements
1. **Build order optimization using topological sorting**: The tool must analyze module dependencies to determine optimal build order, using topological sorting to identify which components can be built in parallel while respecting dependency constraints.

2. **Incremental build impact analysis for changed files**: Critical for CI/CD efficiency, the system must trace which modules are affected by file changes, providing precise lists of components that need rebuilding to minimize unnecessary compilation.

3. **Parallel compilation opportunity identification**: Essential for build time reduction, the tool must identify independent module clusters that can be compiled simultaneously, calculating optimal parallelization strategies based on dependency depth and build resources.

4. **Test suite dependency mapping for selective testing**: To optimize test execution, the system must map which tests depend on which modules, enabling selective test runs based on changed code and reducing overall pipeline duration.

5. **Binary artifact caching strategy based on dependencies**: For maximum efficiency, the tool must analyze dependency stability to recommend caching strategies, identifying which artifacts can be cached long-term versus those requiring frequent rebuilds.

## Technical Requirements
- **Testability requirements**: All build optimization algorithms must be unit testable with mock dependency graphs and build scenarios. Integration tests should verify correctness against real build systems.
- **Performance expectations**: Must analyze dependency graphs with 10,000+ nodes in under 30 seconds. Build impact analysis should complete in milliseconds for incremental changes.
- **Integration points**: Must integrate with popular build systems (Make, Bazel, CMake), CI/CD platforms (Jenkins, GitHub Actions), and provide APIs for custom build tool integration.
- **Key constraints**: Must handle various build system formats, work with incomplete build definitions, and provide meaningful results for both interpreted and compiled Python projects.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must parse project dependencies to create build graphs, apply topological sorting for build order optimization, calculate minimal rebuild sets for file changes, identify parallelization opportunities with resource constraints, map test dependencies for selective execution, and generate caching strategies based on change frequency. The system should support various build system formats and provide real-time build optimization recommendations.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Correct topological sorting with cycle detection
  - Accurate incremental build impact calculation
  - Valid parallel build opportunity identification
  - Proper test dependency mapping
  - Effective caching strategy generation

- **Critical user scenarios that should be tested**:
  - Optimizing a monorepo build with 1000+ packages
  - Reducing CI time for a microservices project
  - Implementing selective testing for a large test suite
  - Parallelizing builds for a scientific computing project
  - Caching strategy for a frequently updated library

- **Performance benchmarks that must be met**:
  - Generate build order for 10,000 modules in under 20 seconds
  - Calculate incremental build impact in under 100ms
  - Identify parallel build opportunities in under 5 seconds
  - Map test dependencies for 100,000 tests in under 60 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Circular dependencies in build graphs
  - Dynamic dependencies determined at build time
  - Platform-specific build requirements
  - Missing or corrupted build artifacts
  - Resource-constrained build environments

- **Required test coverage metrics**:
  - Minimum 95% code coverage for graph algorithms
  - 100% coverage for topological sorting implementation
  - Full coverage of caching strategy logic
  - Integration tests for major build systems

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
Clear metrics and outcomes that would indicate the implementation successfully meets this persona's needs:
- Reduces build times by 60% through parallelization
- Achieves 90% cache hit rate with recommended caching strategy
- Decreases test execution time by 70% through selective testing
- Identifies 95% of safe parallel build opportunities
- Enables incremental builds that are 10x faster than full builds

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
From within the project directory, set up the development environment:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```