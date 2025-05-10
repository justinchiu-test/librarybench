# Open Source Project Documentation Generator

A specialized static site generator for open source projects that keeps documentation synchronized with code and provides comprehensive resources for contributors and users.

## Overview

This project is a Python library for creating and maintaining documentation websites for open source software projects. It focuses on tight integration with code repositories, automated documentation generation, and comprehensive contributor resources that stay synchronized with project evolution.

## Persona Description

Raj maintains several open source libraries and needs to create comprehensive project websites with documentation, guides, community resources, and contribution instructions that stay synchronized with the code.

## Key Requirements

1. **GitHub Repository Integration**: Implement a system to pull README files, contributor guides, and issue templates directly from GitHub repositories. This integration ensures that Raj's documentation remains synchronized with the source repository, preventing drift between documentation and code while allowing contributors to submit fixes to both code and documentation through the same workflow.

2. **Changelog Generation System**: Create an automated system for generating formatted release notes from commit history and release tags. This feature saves Raj significant manual effort by transforming raw commit logs into organized, readable release notes that highlight new features, bug fixes, and breaking changes based on commit patterns and tags.

3. **Documentation Testing Framework**: Implement a verification system that ensures code examples in documentation actually work with current library versions. This testing framework is critical for Raj to maintain documentation quality, as it automatically catches examples that become outdated due to API changes, preventing frustration for users who try to follow documentation that no longer works.

4. **Contributor Recognition System**: Develop a feature that automatically highlights project contributors with their contributions across documentation, code, and community support. This recognition is important for building and maintaining Raj's open source community, as it acknowledges the value of all contribution types and motivates continued participation.

5. **Dependency Documentation Generator**: Create a system that automatically documents library dependencies, version requirements, and compatibility information. This feature helps users of Raj's libraries understand dependency constraints, potential conflicts, and versioning requirements, reducing issues related to dependency management and incompatible versions.

## Technical Requirements

- **Testability Requirements**:
  - GitHub integration must be mockable for testing without actual API access
  - Changelog generation must produce consistent output from deterministic inputs
  - Documentation testing must verify code examples against actual library behavior
  - Contributor recognition must handle various contribution patterns
  - Dependency documentation must accurately reflect project requirements

- **Performance Expectations**:
  - Full documentation generation should complete in under 2 minutes for typical projects
  - GitHub data fetching should use efficient caching to minimize API calls
  - Documentation testing should run in parallel where possible
  - Incremental builds should only process changed files
  - The system should handle projects with 1000+ files and 100+ contributors

- **Integration Points**:
  - GitHub API for repository content and contributor data
  - Version control systems for historical information
  - Package management systems for dependency information
  - Documentation linting and validation tools
  - Code execution environments for example testing

- **Key Constraints**:
  - API rate limits for GitHub must be respected with appropriate throttling
  - Documentation testing must run in isolated environments
  - Generated sites must work without JavaScript for core functionality
  - All processing must be reproducible in CI/CD environments
  - Security considerations for fetching and executing external code

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Repository Synchronization System**:
   - Fetch content from GitHub repositories (README, guides, templates)
   - Convert between different markdown flavors when necessary
   - Handle relative links and assets correctly
   - Maintain synchronization between local content and repository state

2. **Release Documentation Pipeline**:
   - Parse commit history and extract meaningful changes
   - Categorize changes (features, fixes, breaking changes)
   - Generate formatted changelogs with proper linking
   - Support customizable changelog templates and formats

3. **Documentation Verification System**:
   - Extract code examples from documentation
   - Set up isolated execution environments
   - Verify example output against expected results
   - Report and highlight documentation/code inconsistencies

4. **Contributor Management System**:
   - Collect contributor information from various sources
   - Generate contribution statistics and visualizations
   - Create contributor profiles with their contributions
   - Support various recognition methods and layouts

5. **Dependency Analysis Framework**:
   - Parse project dependency information
   - Generate compatibility matrices and version requirements
   - Document known conflicts and workarounds
   - Provide upgrade paths and dependency relationships

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate fetching and rendering of repository content
  - Correct changelog generation from git history
  - Successful verification of documentation examples
  - Proper recognition of different contribution types
  - Accurate dependency documentation generation

- **Critical User Scenarios**:
  - Project maintainer updates documentation after API changes
  - New release requires updated changelog and compatibility information
  - Documentation examples need verification after dependency updates
  - New contributors need to be recognized in the project website
  - Users need to understand dependency requirements for different versions

- **Performance Benchmarks**:
  - Repository synchronization time for projects of various sizes
  - Changelog generation time for repositories with extensive history
  - Documentation testing time for different numbers of code examples
  - Build time for incremental vs. full documentation generation

- **Edge Cases and Error Conditions**:
  - Handling of API rate limiting and temporary failures
  - Processing malformed or inconsistent git history
  - Management of documentation examples that cannot be automatically verified
  - Handling of contributors with multiple identities or limited information
  - Recovery from interrupted build processes

- **Required Test Coverage**:
  - 90% code coverage for core library functions
  - 100% coverage for GitHub integration components
  - 95% coverage for changelog generation logic
  - 95% coverage for documentation testing framework
  - 90% coverage for dependency documentation generation

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Documentation consistently stays synchronized with repository content
2. Changelogs are automatically generated with proper categorization and formatting
3. Code examples in documentation are verified to work with current library versions
4. Contributors are properly recognized for their various types of contributions
5. Dependency requirements and compatibility information is clearly documented
6. The entire process integrates smoothly with continuous integration workflows
7. All tests pass with at least 90% code coverage
8. The system can be used by open source projects of varying sizes and complexities

To set up your development environment:
```
uv venv
source .venv/bin/activate
```