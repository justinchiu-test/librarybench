# Open Source Project Documentation Generator

A specialized static site generator designed for open source maintainers to create comprehensive project websites that stay synchronized with code repositories, changelog history, and contributor information.

## Overview

This project implements a Python library for generating open source project websites that integrate directly with code repositories. It focuses on the needs of project maintainers who need to maintain up-to-date documentation, guides, and project information that stays synchronized with the actual codebase.

## Persona Description

Raj maintains several open source libraries and needs to create comprehensive project websites with documentation, guides, community resources, and contribution instructions that stay synchronized with the code.

## Key Requirements

1. **GitHub Integration**: Implement direct integration with GitHub repositories to pull README files, contributor guides, issue templates, and other documentation directly from the repository.
   - Critical for Raj because it ensures documentation stays synchronized with the code, eliminating duplication and reducing maintenance overhead when project information changes.
   - Must support authentication, rate limiting, and caching for efficient repository access.

2. **Changelog Generation**: Create a system for generating formatted release notes from commit history and release tags with proper categorization and formatting.
   - Essential for Raj because manually maintaining changelogs is time-consuming and error-prone, while automatic generation ensures completeness and consistency.
   - Should categorize changes (features, fixes, breaking changes) and link to relevant issues and pull requests.

3. **Live Documentation Testing**: Implement functionality to verify that code examples in documentation actually work with current library versions.
   - Important for Raj because outdated or incorrect code examples in documentation cause confusion for users and increase support burden.
   - Must execute code snippets in a controlled environment and report failures.

4. **Contributor Acknowledgment**: Create a system for showcasing project contributors with their contributions, activity, and recognition of specific contributions.
   - Valuable for Raj because acknowledging contributors is important for community building and motivation, and manual tracking becomes unmanageable as the project grows.
   - Should extract contributor information from repository history and present it in a meaningful way.

5. **Dependency Documentation**: Automatically document library dependencies, version requirements, and potential compatibility issues.
   - Critical for Raj because users need clear information about dependencies and compatibility to successfully use the library, and this information frequently changes with new releases.
   - Must extract dependency information from project configuration and present it with proper formatting and organization.

## Technical Requirements

### Testability Requirements
- All components must be individually testable with clear interfaces
- Mock GitHub API responses for testing repository integration
- Support snapshot testing for generated documentation
- Test code snippet execution with various versions of dependencies
- Validate changelog generation with realistic commit histories

### Performance Expectations
- Complete documentation build should finish in under 30 seconds for typical repositories
- GitHub API interactions should be optimized with proper caching
- Code snippet testing should execute 50+ snippets in under 60 seconds
- Contributor analysis should handle repositories with 500+ contributors efficiently
- Generated sites should achieve 90+ scores on web performance metrics (to be simulated in tests)

### Integration Points
- GitHub API for repository data extraction
- Git for local repository analysis
- Package managers for dependency information
- Code execution environments for documentation testing
- Markdown processing for README and other documentation files

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must handle GitHub API rate limiting gracefully
- Documentation testing must execute code without security risks
- Must work with both local repositories and remote GitHub repositories
- Generated documentation must be accurate and synchronized with actual code
- Must respect GitHub Terms of Service and API usage guidelines

## Core Functionality

The Open Source Project Documentation Generator should provide a comprehensive Python library with the following core capabilities:

1. **Repository Integration System**
   - Connect to GitHub repositories using API tokens or public access
   - Extract documentation files, READMEs, and contribution guides
   - Process issue and pull request templates
   - Monitor repository changes for documentation updates
   - Cache repository data for efficient builds

2. **Changelog Management**
   - Parse git commit history with semantic versioning
   - Extract release information from tags and releases
   - Categorize changes based on commit messages or PR labels
   - Generate formatted changelogs with proper attribution
   - Link changes to relevant issues and pull requests

3. **Documentation Testing Engine**
   - Extract code examples from documentation files
   - Set up isolated environments for testing code snippets
   - Execute snippets against actual library code
   - Report success or failure with context
   - Suggest fixes for failing examples

4. **Contributor Recognition System**
   - Extract contributor information from repository history
   - Calculate contribution statistics and activity metrics
   - Generate contributor profiles with relevant information
   - Support for highlighting specific contributions or roles
   - Implement proper attribution and acknowledgment

5. **Dependency Analysis**
   - Parse project configuration files for dependency information
   - Extract version requirements and compatibility constraints
   - Generate formatted dependency documentation
   - Check for potential conflicts or issues
   - Provide upgrade path information

## Testing Requirements

### Key Functionalities to Verify

1. **GitHub Repository Integration**
   - Test connection and authentication with GitHub API
   - Verify extraction of various documentation elements
   - Test rate limit handling and caching mechanisms
   - Confirm proper error handling for missing or inaccessible files
   - Verify WebHook handling for documentation updates

2. **Changelog Generation**
   - Test parsing of commit histories with various formats
   - Verify categorization of changes (features, fixes, etc.)
   - Test proper formatting of changelogs for different release types
   - Confirm linking to issues and pull requests
   - Verify handling of incomplete or ambiguous commit messages

3. **Documentation Testing**
   - Test extraction of code snippets from various formats
   - Verify execution environment setup and isolation
   - Test snippet execution with various library versions
   - Confirm proper reporting of success and failure
   - Verify handling of dependencies and imports in snippets

4. **Contributor Management**
   - Test extraction of contributor information from repositories
   - Verify calculation of contribution metrics
   - Test generation of contributor pages and acknowledgments
   - Confirm handling of deleted accounts or renamed users
   - Verify proper attribution for various contribution types

5. **Dependency Documentation**
   - Test extraction of dependency information from various formats
   - Verify formatting and organization of dependency lists
   - Test version compatibility checking
   - Confirm handling of complex dependency trees
   - Verify updates when dependencies change

### Critical User Scenarios

1. Generating a complete project website from a GitHub repository with all documentation elements
2. Creating a properly formatted changelog after a new release with various types of changes
3. Testing documentation examples against a new library version and identifying broken examples
4. Updating contributor information after significant new contributions
5. Documenting dependencies after adding or changing library requirements

### Performance Benchmarks

- Complete documentation build should finish in under 30 seconds for typical repositories
- GitHub API requests should be batched and optimized to stay within rate limits
- Documentation testing should execute 50+ code snippets in under 60 seconds
- Contributor analysis should process 500+ contributors in under 10 seconds
- Incremental builds should complete in under 5 seconds for small changes

### Edge Cases and Error Conditions

- Test handling of GitHub API rate limiting and service outages
- Verify behavior with repositories containing thousands of commits
- Test with malformed or non-standard commit messages
- Verify handling of code examples that timeout or consume excessive resources
- Test with complex dependency trees and version conflicts
- Validate behavior with repositories that have unusual structures or missing key files

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for GitHub integration logic
- 100% coverage for changelog generation
- Integration tests for the entire documentation pipeline
- Performance tests for both small and large repositories

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

The Open Source Project Documentation Generator will be considered successful if it:

1. Correctly integrates with GitHub repositories to pull and synchronize documentation
2. Generates properly formatted changelogs from commit history and release tags
3. Successfully tests code examples in documentation against actual library code
4. Creates accurate contributor acknowledgment pages with proper attribution
5. Automatically documents dependencies with version requirements and compatibility information
6. Builds documentation sites efficiently with proper cross-linking and organization
7. Produces accessible, developer-friendly HTML output
8. Maintains documentation that stays synchronized with code changes

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.