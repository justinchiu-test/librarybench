# Unified Command-Line Task Manager

A command-line task management tool that combines functionality for both researchers and security analysts, built on a unified library.

## Features

- Create, update, list, and delete tasks
- Support for both research tasks and security findings
- Tag tasks for easy organization
- Add notes to tasks
- Filter tasks by type, status, priority, or tags
- Flexible output formats (text or JSON)
- Customizable metadata for specialized fields
- Task persistence to file storage with optional encryption
- Parent-child task relationships
- Secure storage with integrity verification

## Installation

1. Clone the repository
2. Install dependencies:
```
pip install -e .
```

## Usage

The task manager provides a simple command-line interface for managing tasks.

### Basic Commands

```bash
# Show help
./cli_persistent.py --help

# Create a new task
./cli_persistent.py create --title "Implement feature X" --description "Add support for X"

# Create a research task with specialized fields
./cli_persistent.py create --title "Literature review" --description "Review papers" --type research --estimated-hours 4

# Create a security task with specialized fields
./cli_persistent.py create --title "SQL Injection vulnerability" --description "Found SQL injection in login form" --type security --severity "Critical" --affected-systems "auth-service,user-api"

# List all tasks
./cli_persistent.py list

# List tasks filtered by type, status, or tag
./cli_persistent.py list --type research
./cli_persistent.py list --status in_progress
./cli_persistent.py list --tag important

# Get detailed information about a task
./cli_persistent.py get <task-id>

# Update a task
./cli_persistent.py update <task-id> --title "New title" --status completed

# Add a note to a task
./cli_persistent.py note <task-id> "Made progress on this task"

# Add a tag to a task
./cli_persistent.py add-tag <task-id> urgent

# Remove a tag from a task
./cli_persistent.py remove-tag <task-id> urgent

# Delete a task
./cli_persistent.py delete <task-id>
```

### JSON Output

Add the `--json` flag to the `list` or `get` commands to output in JSON format:

```bash
./cli_persistent.py list --json
./cli_persistent.py get <task-id> --json
```

### Demo Script

To see a comprehensive demonstration of the CLI functionality, run:

```bash
./demo_persistent.py
```

This script will:
1. Create tasks of different types (generic, research, security)
2. List tasks with various filters
3. Get detailed task information
4. Update tasks and change statuses
5. Add and remove notes and tags
6. Delete tasks

## Task Types

The unified task manager supports three types of tasks:

1. **Generic tasks** - Basic tasks with title, description, status, and priority
2. **Research tasks** - Extended tasks with research-specific fields like estimated hours and actual hours
3. **Security tasks** - Extended tasks with security-specific fields like severity, affected systems, and discoverer

## Library Architecture

The unified task manager is built on a common library that provides:

- Base models for entities and tasks
- Common storage interfaces (in-memory and file-based)
- Shared service layer components
- Unified security utilities for encryption and integrity verification
- Reusable validation helpers

The library architecture enables:

- Consistent behavior across all task types
- Reduced code duplication
- Flexible extension points for specific use cases
- Type-safe interfaces
- Standardized error handling
- Secure data handling with cryptographic protection

### Common Package Structure

```
common/
├── core/
│   ├── models.py    # Base models and common data structures
│   ├── storage.py   # Storage interface and implementations
│   ├── service.py   # Service base classes
│   ├── security.py  # Security-related functionality
│   └── utils.py     # Shared utility functions
```

## Development

To extend the task manager with additional functionality:

1. Add new task types by extending the `BaseTask` model in `common.core.models`
2. Implement storage backends by extending the `BaseStorageInterface` class in `common.core.storage`
3. Add service layer components by extending the `BaseService` or `BaseTaskService` classes in `common.core.service`
4. Create new command handlers in the `commands.py` file
5. Update the argument parser in `create_parser()` to support new commands

## Persona Implementations

The unified library is currently used by two persona implementations:

1. **ResearchTrack**: Task manager for researchers with specialized fields for research questions, time tracking, and research artifact associations.
2. **SecureTask**: Task manager for security analysts with specialized fields for findings, evidence management, and compliance tracking.

Both implementations extend the common library classes while adding domain-specific functionality.

## Testing

To run tests:

```bash
pytest tests/ --json-report --json-report-file=report.json
```

## License

MIT