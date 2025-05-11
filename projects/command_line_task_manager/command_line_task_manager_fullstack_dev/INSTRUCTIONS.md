# GitTask - Git-Integrated CLI Task Management for Developers

## Overview
A specialized command-line task management system designed for full-stack developers working across multiple client projects. This system seamlessly integrates with git workflows, enabling developers to associate tasks with specific commits and branches, organize project-specific tasks, and maintain productivity without disrupting coding flow.

## Persona Description
Rachel builds web applications across multiple client projects simultaneously and needs to track numerous development tasks without disrupting her coding flow. Her primary goal is to organize project-specific tasks and seamlessly integrate task management with her git workflow to associate tasks with specific commits and branches.

## Key Requirements
1. **Git Integration**: Implement a sophisticated integration with git that automatically links tasks to commits and branches. This feature is critical for Rachel as it enables her to maintain a clear connection between tasks and their implementation in code, streamline her development workflow by reducing context switching, and create an auditable history of which code changes fulfill which requirements.

2. **Project-Based Context Switching**: Develop context-aware functionality that automatically filters tasks based on the current working directory. This capability is essential for Rachel to maintain focus on the relevant tasks for the current project she's working on, eliminate mental overhead of task filtering, and instantly switch contexts when moving between different client codebases.

3. **Task Templating System**: Create a flexible templating system for common development workflows (bug fixes, features, refactoring). This feature allows Rachel to standardize task creation across different types of work, ensure consistent information capture for similar types of tasks, and save time when initiating new development work with predefined templates.

4. **IDE Terminal Integration**: Design a clean API that supports integration with VS Code/WebStorm terminal environments. This integration enables Rachel to access task information directly within her development environment, maintain her workflow without switching applications, and increase productivity by keeping task management within her existing tools.

5. **PR/Commit Message Generation**: Build functionality to automatically generate pull request descriptions and commit messages based on completed task details. This feature helps Rachel maintain high-quality documentation of code changes, ensure PR descriptions properly reference requirements and implementation details, and save time on repetitive documentation tasks.

## Technical Requirements

### Testability Requirements
- Git integration must be testable with mock repositories
- Directory-based context switching must be testable with simulated filesystem
- Task template rendering must be verifiable with predefined inputs and expected outputs
- IDE integration API must be fully testable without requiring actual IDE environments
- Message generation must be testable with predefined task data and expected output formats
- All components must be unit testable in isolation

### Performance Expectations
- Context switching based on directory must occur in <100ms
- Git operations must add <200ms overhead to normal git commands
- Template rendering must complete in <50ms
- Task querying and filtering must handle repositories with 10,000+ tasks
- System must support at least 50 distinct project contexts without performance degradation

### Integration Points
- Git hooks for commit and branch operations
- Filesystem monitoring for directory changes
- Template engine with variable substitution
- External API for IDE plugins
- PR platform integration (GitHub, GitLab, Bitbucket)

### Key Constraints
- Git integration must not interfere with normal git operations
- All functionality must be accessible via programmatic API without UI components
- The implementation must not require admin privileges
- Task data must be storable within git repositories (optional) or externally
- The system must maintain data integrity across branch switches and merges

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Task Management Engine**: A core module handling CRUD operations for tasks with support for attributes like title, description, status, priority, and custom fields.

2. **Git Integration Layer**: Functionality to link tasks with git operations, including commit association, branch tracking, and task status updates based on git activities.

3. **Context Detection System**: A component that detects the current working directory and project context, automatically filtering and presenting relevant tasks.

4. **Template Management**: A flexible template system for different task types with variable substitution and default values based on context.

5. **IDE Integration API**: A well-defined API that exposes task operations in a format suitable for consumption by IDE terminal environments.

6. **Message Generation Engine**: Logic to transform task information into formatted commit messages and pull request descriptions according to configurable templates.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by a CLI tool (though implementing the CLI itself is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Task creation, retrieval, updating, and deletion with all required attributes
- Git hook integration with proper task linking
- Directory-based context detection and task filtering
- Template rendering with variable substitution
- API endpoints for IDE integration
- Message generation with proper formatting

### Critical User Scenarios
- Complete development workflow from task creation to commit to PR submission
- Switching between multiple client projects with automatic context changes
- Using templates for different types of development tasks
- Accessing task information from within the IDE terminal
- Generating appropriate documentation for code changes

### Performance Benchmarks
- Context switching must occur in <100ms
- Task operations must complete in <50ms
- Git integration operations must add <200ms to normal git command execution
- The system must maintain performance with 50+ projects and 10,000+ tasks
- Template rendering must process at least 20 templates per second

### Edge Cases and Error Conditions
- Handling of git merge conflicts affecting task data
- Proper behavior when switching to unknown project contexts
- Recovery from interrupted git operations
- Handling malformed templates or template data
- Graceful degradation when IDE integration is unavailable
- Proper error reporting for failed git operations

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Integration tests must verify git hook behavior

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
2. The system demonstrates seamless integration with git, automatically associating tasks with commits and branches.
3. Project context switching works correctly based on the current working directory.
4. Task templates can be created, used, and customized for different development workflows.
5. The API for IDE integration is well-documented and functional.
6. PR and commit message generation produces appropriate content based on task information.
7. All performance benchmarks are met under the specified load conditions.
8. The implementation maintains data integrity across git operations like branch switching and merging.

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