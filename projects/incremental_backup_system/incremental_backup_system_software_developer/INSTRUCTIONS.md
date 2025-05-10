# CodeVault - Intelligent Backup System for Developers

## Overview
CodeVault is a specialized incremental backup system tailored for software developers who manage multiple client projects. It intelligently tracks code changes, integrates with version control systems, and provides powerful tools for organizing, scheduling, and retrieving code snapshots while minimizing storage requirements.

## Persona Description
Mariana is a freelance software developer managing multiple client projects simultaneously on her laptop. She needs a reliable backup system that can intelligently track project file changes without consuming excessive storage space while allowing her to reference or restore previous versions of code.

## Key Requirements

1. **Programming Language-Aware Backup Policies**
   - Implement smart detection and prioritization of source code files, configuration files, and project assets
   - Create customizable backup policies that recognize file patterns by language (.py, .js, .json, etc.)
   - Allow higher backup frequency for critical development files while reducing backup frequency for build artifacts
   - Support intelligent exclusion patterns that understand common build directories and dependencies
   - This feature is critical as it ensures that Mariana's source code is backed up frequently while avoiding wasteful backups of generated files

2. **Version Control System Integration**
   - Develop intelligent detection of Git, Mercurial, and SVN repositories
   - Implement policy options to exclude, include, or specially handle version-controlled files
   - Create backup strategies for non-committed changes that complement version control
   - Support capturing version control metadata for better context in restores
   - This feature prevents redundant backups of files already tracked in version control while ensuring uncommitted work is never lost

3. **Project-Based Organization**
   - Design a tagging and grouping system for related files across different directories
   - Implement project configuration files that define logical boundaries of projects
   - Support automatic detection of project structures for common frameworks
   - Create APIs for custom project grouping rules
   - This organization system is essential for Mariana to logically group client projects that may span multiple directories or repositories

4. **Intelligent Backup Scheduling**
   - Develop heuristics to detect active coding sessions based on file modification patterns
   - Implement triggers for backup after significant changes or reaching thresholds
   - Create a resource-aware scheduling system that avoids backup during high CPU/memory usage
   - Support time windows for more intensive backup operations
   - This feature prevents disruption during active development while ensuring timely backups after significant work sessions

5. **Code Pattern Cross-Reference Tools**
   - Create a searchable index of backed-up code content
   - Implement regex and AST-based searching across backup history
   - Develop timeline visualization for when specific code patterns were introduced or modified
   - Support diffing between any two backup points for specific files or patterns
   - This feature allows Mariana to track when specific code patterns were introduced or changed, critical for debugging and understanding code evolution

## Technical Requirements

### Testability Requirements
- All components must be designed with testability in mind with clear separation of concerns
- Backup engine must be mockable to test scheduling without actual file operations
- File system operations should be abstracted to support testing with virtual file systems
- All detection heuristics must be testable with simulated file change patterns
- Search and indexing must be testable with predefined code corpus

### Performance Expectations
- Backup operations should impact system performance minimally during active development
- Indexing and search operations should complete in under 5 seconds for projects up to 100,000 files
- Delta storage algorithm should achieve at least 90% space reduction for typical code changes
- Backup initialization for a new 1GB project should take no more than 60 seconds on standard hardware
- RAM usage should never exceed 500MB even when processing large projects

### Integration Points
- Version control systems (Git, Mercurial, SVN) via their command-line interfaces or libraries
- File system monitoring using efficient OS-specific APIs for change detection
- Editor plugins interface for detecting active editing sessions (optional extension point)
- Output formats compatible with diff and code analysis tools
- Support for external storage backends via a plugin architecture

### Key Constraints
- All backup operations must be atomic - either complete successfully or roll back entirely
- Must work offline without any cloud dependencies
- Backup format must be open and documented to prevent vendor lock-in
- All code indexing must respect .gitignore and similar exclusion patterns
- System must be resilient to unexpected shutdowns during backup operations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide these core capabilities:

1. **Backup Engine**
   - Efficient incremental backup implementation with delta encoding
   - File change detection and checksumming
   - Metadata preservation for all relevant file attributes
   - Atomic backup operations with journaling for crash recovery

2. **Project Management**
   - Project definition and boundary detection
   - Customizable grouping and tagging system
   - Configuration file parsing and validation
   - Project statistics and reporting

3. **Code-Aware Processing**
   - Language detection and classification
   - Syntax-aware differencing for efficient storage
   - Build artifact detection
   - Version control awareness

4. **Intelligent Scheduling**
   - Activity detection algorithms
   - Resource usage monitoring
   - Configurable triggers and thresholds
   - Logging and notification system

5. **History and Search**
   - Backup history indexing
   - Content-based search capabilities
   - Pattern matching across versions
   - Timeline generation and analysis

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection and classification of programming language files
- Correct integration behavior with version control systems
- Proper functioning of project grouping and organization
- Effectiveness of the activity detection and scheduling logic
- Accuracy and performance of code pattern search functionality

### Critical User Scenarios
- Daily development workflow with multiple editing sessions
- Project switching between multiple client codebases
- Restoration of specific code versions after accidental changes
- Searching for the history of a particular code pattern
- Recovery from system crash during backup operation

### Performance Benchmarks
- Backup speed: Initial backup of 1GB project under 60 seconds
- Incremental backup: Small code changes (under 100 files) backed up in under 10 seconds
- Search performance: Code pattern searches complete in under 5 seconds
- Storage efficiency: Achieve 10:1 compression ratio for year-long backup history
- Resource usage: CPU usage below 15% during background backup operations

### Edge Cases and Error Conditions
- Sudden power loss during backup operations
- Corrupted backup repository detection and recovery
- Extremely large files or projects exceeding normal parameters
- Invalid or conflicting project configurations
- File permission issues and locked files
- Handling of symlinks, hardlinks, and special files

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core modules
- 100% coverage for critical paths including error handling
- Performance tests must cover all operations with large datasets
- All public APIs must have comprehensive integration tests
- Fuzz testing for file parser components

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. A developer can define custom backup policies for different programming languages and project types with minimal configuration
2. The system correctly identifies and appropriately handles files already under version control
3. Projects can be logically organized and grouped regardless of their filesystem location
4. Backups automatically occur after significant development sessions without manual intervention
5. A developer can easily search through backup history to find when specific code patterns were introduced or modified
6. All backups maintain perfect fidelity when restored, including metadata and file relationships
7. The system uses minimal storage space through efficient delta encoding and deduplication
8. Performance impact on development activities is negligible
9. All operations are reliable with proper error handling and recovery mechanisms
10. The system passes all the defined test suites with the required coverage metrics

To get started with implementation:
1. Set up a Python virtual environment: `uv venv`
2. Activate the environment: `source .venv/bin/activate`
3. Install development dependencies
4. Implement the core modules following the requirements
5. Create comprehensive tests for all functionality