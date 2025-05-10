# DevFlow Task Manager - A Full-Stack Developer's Task Management Library

## Overview
DevFlow Task Manager is a specialized task management library designed specifically for full-stack developers who work across multiple client projects simultaneously. It provides robust APIs to organize project-specific tasks, integrate with git workflows, and maintain productivity without disrupting coding flow. The library enables seamless context switching between projects and automates common development workflow tasks.

## Persona Description
Rachel builds web applications across multiple client projects simultaneously and needs to track numerous development tasks without disrupting her coding flow. Her primary goal is to organize project-specific tasks and seamlessly integrate task management with her git workflow to associate tasks with specific commits and branches.

## Key Requirements
1. **Git Integration**: The library must provide seamless integration with git, automatically linking tasks to commits and branches. This is critical for Rachel to maintain context between her task management and code changes, ensuring that each development activity is properly documented and traceable to specific code modifications.

2. **Project-based Context Switching**: The system must support automatic filtering of tasks based on the current working directory. This feature is essential for Rachel to maintain focus on relevant tasks when switching between different client projects, reducing cognitive load and improving productivity.

3. **Task Templates for Development Workflows**: The library must provide flexible templating for common development activities such as bug fixes, feature implementations, and refactoring tasks. This feature is crucial for Rachel to quickly create structured tasks that follow consistent patterns across different projects.

4. **IDE Terminal Integration**: The system should provide compatibility with terminal interfaces in common IDEs like VSCode and WebStorm. This integration is vital for Rachel's workflow as it allows her to manage tasks directly within her development environment without context switching.

5. **PR/Commit Message Generation**: The library must offer automatic generation of pull request descriptions and commit messages based on completed task details. This functionality is important for Rachel to maintain consistent and informative version control documentation that reflects the work completed.

## Technical Requirements
- **Testability Requirements**:
  - All components must be individually testable with mock integrations
  - Git integration functionality must be testable without requiring actual git repositories
  - Task context switching must be verifiable with simulated directory changes
  - Template functionality must be comprehensively testable for different workflow types
  - PR/commit message generation must be testable with predefined task data

- **Performance Expectations**:
  - Task retrieval by project context must operate in under 30ms
  - Git integration operations should complete within 100ms
  - The system must handle at least 5,000 tasks across multiple projects
  - Context switching between projects must be nearly instantaneous
  - Template application should be performant even with complex task structures

- **Integration Points**:
  - Git version control system via gitpython or similar libraries
  - Filesystem for project directory detection
  - IDE terminal interfaces
  - Pull request API endpoints (GitHub, GitLab, etc.)
  - Task storage and retrieval system

- **Key Constraints**:
  - No direct UI components (API-only implementation)
  - Must maintain backward compatibility with various git versions
  - Should function in offline mode when git remote is unavailable
  - Filesystem access must be efficient and non-blocking
  - Must respect git configuration and not interfere with existing workflows

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The library must provide the following core functionality:

1. **Task Management System**: 
   - Create, read, update, and delete tasks with appropriate metadata
   - Support for task prioritization, categorization, and status tracking
   - Association of tasks with specific projects and clients
   - Time tracking for development tasks

2. **Git Integration**: 
   - Track associations between tasks and git branches
   - Link commits to specific tasks automatically
   - Parse commit history to update task statuses
   - Support for different git workflows (feature branches, trunk-based development)

3. **Context-Aware Task Filtering**: 
   - Detect current working directory and project context
   - Filter and present only relevant tasks based on context
   - Support for quick context switching between projects
   - Save and restore context states

4. **Development Workflow Templates**: 
   - Define and manage templates for common development tasks
   - Support custom template creation and modification
   - Apply templates with project-specific parameters
   - Track template usage and effectiveness

5. **Message Generation**: 
   - Generate commit messages from task details
   - Create pull request descriptions with task context
   - Support for customizable message templates
   - Include relevant task metadata in generated content

## Testing Requirements
To validate a successful implementation, the following testing should be conducted:

- **Key Functionalities to Verify**:
  - Task creation, retrieval, updating, and deletion
  - Git integration and automatic task-commit linking
  - Context detection and task filtering
  - Template application for different workflow types
  - PR/commit message generation

- **Critical User Scenarios**:
  - Creating a task in a specific project context
  - Associating a task with a git branch and commits
  - Switching between projects and observing correct task filtering
  - Applying a template for a bug fix workflow
  - Generating a PR description from completed task details

- **Performance Benchmarks**:
  - Task retrieval by context < 30ms
  - Git operation integrations < 100ms
  - Context switching < 10ms
  - Template application < 50ms
  - PR generation < 200ms

- **Edge Cases and Error Conditions**:
  - Handling projects without git repositories
  - Managing tasks when working directory is not a recognized project
  - Recovering from git operation failures
  - Handling merge conflicts in task-associated branches
  - Dealing with malformed task data

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all modules
  - 100% coverage for git integration components
  - All public APIs must have comprehensive test cases
  - All error handling code paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
A successful implementation of the DevFlow Task Manager will meet the following criteria:

1. **Functionality Completeness**:
   - All five key requirements are fully implemented and operational
   - Git integration works seamlessly with various workflows
   - Context switching correctly filters tasks by project
   - Templates support all common development workflows
   - PR/commit message generation produces useful content

2. **Performance Metrics**:
   - All performance benchmarks are met or exceeded
   - The system handles multiple projects with thousands of tasks
   - Context switching is instantaneous from the user's perspective

3. **Quality Assurance**:
   - Test coverage meets or exceeds the specified metrics
   - All identified edge cases and error conditions are properly handled
   - No critical bugs in core functionality

4. **Integration Capability**:
   - The library integrates cleanly with git workflows
   - Task context detection works correctly with project structures
   - IDE terminal compatibility is maintained
   - PR generation works with common code hosting platforms

## Setup Instructions
To set up this project:

1. Use `uv init --lib` to create a proper Python library project structure with a `pyproject.toml` file.

2. Install dependencies using `uv sync`.

3. Run your code with `uv run python script.py`.

4. Run tests with `uv run pytest`.

5. Format code with `uv run ruff format`.

6. Check code quality with `uv run ruff check .`.

7. Verify type hints with `uv run pyright`.