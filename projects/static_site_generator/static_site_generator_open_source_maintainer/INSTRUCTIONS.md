# Open Source Project Documentation Generator

A specialized static site generator optimized for creating comprehensive project websites for open source libraries and tools.

## Overview

This project provides a documentation-focused static site generator that enables open source maintainers to create, maintain, and publish comprehensive project websites with documentation, guides, community resources, and contribution instructions that stay synchronized with the project's codebase.

## Persona Description

Raj maintains several open source libraries and needs to create comprehensive project websites with documentation, guides, community resources, and contribution instructions that stay synchronized with the code.

## Key Requirements

1. **GitHub Integration**: Pull README, contributor guides, and issue templates directly from repositories.
   - As Raj maintains documentation across multiple repositories, direct integration with GitHub ensures that documentation is always up-to-date with the source code without requiring duplicated content management.
   - This feature must support fetching content from specific files, branches, and paths within repositories, integrating them seamlessly into the generated site.

2. **Changelog Generation**: Create formatted release notes from commit history and release tags.
   - Keeping users informed about changes is essential, but manually maintaining changelogs is time-consuming, so Raj needs automatic generation of release notes from Git history.
   - The system should parse conventional commits, release tags, and pull request descriptions to create structured, human-readable changelogs.

3. **Live Documentation Testing**: Verify code examples actually work with current library versions.
   - Documentation is only useful if it accurately reflects the current API, so Raj needs to ensure that code examples actually work with the current versions of his libraries.
   - This feature should extract code examples from documentation, execute them against the current library version, and report any failures.

4. **Contributor Acknowledgment**: Showcase project contributors with their contributions.
   - Recognizing contributors is crucial for community building, so Raj wants to automatically acknowledge everyone who has contributed to his projects.
   - The system should gather contributor information from Git history and GitHub API, organizing them by contribution type and frequency.

5. **Dependency Documentation**: Automatically document library dependencies and requirements.
   - Understanding dependencies is critical for users, so Raj needs to clearly document his libraries' dependencies, their versions, and purpose.
   - This feature should extract dependency information from package files, analyze version requirements, and generate comprehensive dependency documentation.

## Technical Requirements

### Testability Requirements
- GitHub integration must be testable with mock repositories and API responses
- Changelog generation must verify correct parsing of commit history
- Documentation testing must verify example execution and validation
- Contributor acknowledgment must validate correct attribution
- Dependency documentation must verify accurate extraction and formatting

### Performance Expectations
- Repository content synchronization should complete in under 30 seconds per repository
- Changelog generation should process 1000 commits in under 10 seconds
- Documentation testing should verify examples at a rate of at least 5 per second
- Complete site generation should finish in under 60 seconds for a typical open source project
- Contributor data processing should handle repositories with 1000+ contributors

### Integration Points
- GitHub API for repository content and contributor data
- Git version control system for commit history
- Package management systems (npm, pip, etc.) for dependency information
- Code execution environments for testing examples
- Markdown and code parsing libraries

### Key Constraints
- Must operate without persistent server components
- Must generate completely static output deployable to GitHub Pages or similar services
- Must respect GitHub API rate limits and implement proper caching
- Must support incremental builds to minimize API requests and processing time
- Must handle test code execution securely and with proper isolation

## Core Functionality

The system should implement a comprehensive platform for open source project documentation:

1. **Repository Synchronization Engine**
   - Fetch content from GitHub repositories via API
   - Update local content based on repository changes
   - Map repository files to appropriate sections of the documentation
   - Support multiple repositories for multi-package projects

2. **Changelog Management System**
   - Parse Git commit history with conventional commit support
   - Extract metadata from release tags and pull requests
   - Generate structured release notes by version
   - Categorize changes (features, fixes, breaking changes)

3. **Documentation Validation Framework**
   - Extract code examples from documentation files
   - Set up test environments for different languages
   - Execute examples against current library versions
   - Report validation results and errors

4. **Contributor Recognition System**
   - Collect contributor data from Git history and GitHub API
   - Categorize contributions (code, docs, issues, reviews)
   - Generate contributor profiles and acknowledgments
   - Create visualizations of project community

5. **Dependency Analysis**
   - Parse package definition files (package.json, requirements.txt)
   - Resolve dependency versions and relationships
   - Generate dependency graphs and documentation
   - Provide compatibility and version information

## Testing Requirements

### Key Functionalities to Verify
- GitHub repository content synchronization
- Changelog generation from Git history
- Code example extraction and validation
- Contributor data collection and attribution
- Dependency information extraction and documentation

### Critical User Scenarios
- Setting up documentation for a new open source project
- Updating documentation after code changes and new releases
- Testing documentation examples against new library versions
- Acknowledging new contributors automatically
- Updating dependency documentation as requirements change

### Performance Benchmarks
- Sync content from a typical repository (1000 files) in under 30 seconds
- Generate changelogs for 50 releases (1000 commits) in under 10 seconds
- Validate 100 code examples in under 30 seconds
- Process contributor data for 500 contributors in under 15 seconds
- Complete full site generation for a typical project in under 60 seconds

### Edge Cases and Error Conditions
- Handling GitHub API rate limiting and service disruptions
- Managing broken or non-executable code examples
- Processing repositories with unusual commit history or structure
- Handling dependencies with complex version constraints
- Recovering from interrupted build or synchronization processes

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for GitHub integration functionality
- Integration tests for all GitHub API interactions
- Mock-based tests for all external service dependencies
- Performance tests for all time-sensitive operations

## Success Criteria

The implementation will be considered successful if it:

1. Seamlessly synchronizes documentation with GitHub repositories, reflecting changes within 1 build cycle
2. Generates accurate, well-formatted changelogs from conventional commits and release tags
3. Successfully validates at least 95% of code examples against current library versions
4. Properly acknowledges all contributors with appropriate categorization of their contributions
5. Generates comprehensive dependency documentation with accurate version requirements
6. Completes a full documentation build for a typical open source project in under 60 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.