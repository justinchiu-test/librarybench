# CodeVault - Incremental Backup System for Software Development

## Overview
A specialized incremental backup system designed for software developers who manage multiple client projects simultaneously. The system enables intelligent tracking of project file changes, integration with version control systems, and efficient organization of backups while minimizing storage requirements and preserving complete version history.

## Persona Description
Mariana is a freelance software developer managing multiple client projects simultaneously on her laptop. She needs a reliable backup system that can intelligently track project file changes without consuming excessive storage space while allowing her to reference or restore previous versions of code.

## Key Requirements
1. **Programming Language-aware Backup Policies**: Implement flexible, configurable policies that prioritize source code, configuration files, and project assets based on their importance and change frequency. This feature enables Mariana to ensure critical code files receive more frequent backup attention while excluding build artifacts, dependencies, and generated files that can be recreated.

2. **Version Control System Integration**: Create a seamless integration mechanism with common VCS tools (Git, SVN, Mercurial) that avoids duplicating already versioned files while still providing backup for uncommitted changes and project metadata not tracked by VCS. This allows Mariana to maintain comprehensive project backups without wasting storage on files already protected by version control.

3. **Project-based Organization System**: Develop a hierarchical organization scheme that allows logical grouping of related files by project, client, technology stack, and development phase with customizable tagging. This capability enables efficient browsing and restoration by project context rather than just file paths, making it easier to locate specific versions of project components.

4. **Intelligent Backup Scheduling**: Implement automatic detection of active coding sessions that triggers backups after significant change events rather than fixed time intervals. This ensures changes are captured at meaningful development milestones while minimizing disruption during intensive coding sessions.

5. **Code Pattern Cross-referencing**: Create functionality to search across backup history for specific code patterns, functions, or structures to identify when certain code elements were introduced or modified. This feature provides Mariana with powerful forensic capabilities to track the evolution of specific code components across multiple projects and timeframes.

## Technical Requirements

### Testability Requirements
- All components must have isolated unit tests with dependency injection to facilitate mocking
- Backup policy evaluator must be testable with various file types and project structures
- VCS integration must be tested with simulated repository states and configurations
- Scheduling logic must be testable with simulated file system events and coding sessions
- Pattern searching must be verifiable with predetermined code samples and expected matches
- Project organization scheme must be testable with various project hierarchies and relationships

### Performance Expectations
- The system must efficiently handle incremental backups of at least 50 projects (approximately 500,000 files)
- VCS integration must add less than 100ms overhead to backup operations per repository
- Backup operations must complete within 5 minutes for incremental updates to all projects
- Project organization indexing must update in under 3 seconds after file changes
- Pattern searching must return results from a 6-month backup history in under 10 seconds
- File deduplication must achieve at least 60% space reduction for typical development projects

### Integration Points
- Version control system hooks (Git, SVN, Mercurial)
- IDE and text editor activity monitoring
- File system monitoring for real-time change detection
- Programming language parsers for intelligent content analysis
- Build system integration to identify generated artifacts
- Package manager awareness for dependency recognition

### Key Constraints
- The implementation must be portable across Linux, macOS, and Windows
- All operations must be non-blocking to avoid disrupting development workflow
- Storage format must be accessible without specialized tools in emergency situations
- CPU/memory impact must remain under 5% of system resources during normal operation
- Backup operations must gracefully handle concurrent file access conflicts
- Storage use must be self-limiting based on configurable thresholds

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Incremental Backup Engine**: A core module handling file change detection, efficient delta storage, and space-optimized backup creation with complete version history preservation.

2. **Language-aware Policy System**: A flexible framework for defining backup policies based on file types, programming languages, project structures, and modification patterns that optimizes backup frequency and retention.

3. **VCS Bridge**: A set of adapters for interfacing with various version control systems to determine repository status, identify untracked files, and efficiently backup uncommitted changes.

4. **Project Organization Framework**: A logical organization system that maintains relationships between files, projects, and clients independent of physical storage structure to facilitate context-based browsing and restoration.

5. **Activity Detection System**: Intelligence for monitoring development activity across IDEs, editors, and file systems to determine optimal backup timing and prioritization.

6. **Pattern Analysis Engine**: Capability to efficiently search and analyze code patterns across backup history, providing insights into code evolution and facilitating specific version identification.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by a CLI tool (though implementing the CLI itself is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Incremental backup creation, verification, and restoration with perfect fidelity
- Policy-based prioritization of files with appropriate handling of different file types
- Proper integration with VCS tools including handling of various repository states
- Accurate project organization with tagging and relationship maintenance
- Intelligent backup scheduling based on coding activity patterns
- Pattern searching across backup history with relevant results ranking

### Critical User Scenarios
- Complete project migration from one language/framework to another with historical preservation
- Restoration of specific component versions across project evolution
- Recovery of uncommitted changes after system failure
- Identification of code implementation date or author through pattern search
- Storage optimization while maintaining comprehensive history
- Cross-project code reuse identification and tracking

### Performance Benchmarks
- Initial full backup of a 100,000-file project in under 20 minutes
- Incremental backup completing in under a minute for 500 changed files
- Storage efficiency achieving at least 10:1 ratio for historical versions
- Search operations returning results in under 5 seconds for complex patterns
- Project reorganization reflecting in the backup system within 10 seconds
- Less than 200ms latency for checking backup status of any file

### Edge Cases and Error Conditions
- Handling of backup operations during large refactoring sessions
- Recovery from corrupted backup repository with minimal data loss
- Proper functioning with extremely large generated files (e.g., ML models)
- Correct behavior when storage targets become full during backup
- Appropriate handling of symlinks, hardlinks, and unusual file system structures
- Graceful operation during rapid file creation/deletion cycles (e.g., build processes)

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Integration tests must verify all external system interfaces

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
The implementation will be considered successful when:

1. All five key requirements are fully implemented and pass their respective test cases.
2. The system demonstrates the ability to efficiently track and store incremental changes across multiple development projects.
3. Integration with at least one version control system (preferably Git) works seamlessly.
4. The project organization system correctly maintains relationships between related files and projects.
5. Backup scheduling intelligently responds to development activity patterns.
6. Pattern search functionality can locate specific code elements across backup history.
7. All performance benchmarks are met under the specified load conditions.
8. Code quality meets professional standards with appropriate documentation.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup
1. Use `uv venv` to setup a virtual environment. From within the project directory, activate it with `source .venv/bin/activate`.
2. Install the project with `uv pip install -e .`
3. CRITICAL: Before submitting, run the tests with pytest-json-report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```
4. Verify that all tests pass and the pytest_results.json file has been generated.

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.