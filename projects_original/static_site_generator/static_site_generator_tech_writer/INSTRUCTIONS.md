# Technical Documentation Site Generator

A specialized static site generator tailored for creating and maintaining comprehensive technical documentation portals with API references, version control, and interactive code examples.

## Overview

This project implements a Python library for generating technical documentation websites from structured markup files. It focuses on the needs of technical writers who maintain documentation for software projects, providing tools for API reference generation, versioning, code highlighting, interactive examples, and technical diagram creation - all from simple text-based source files.

## Persona Description

Sarah creates comprehensive documentation for open-source software projects and needs to maintain multiple documentation sites with consistent branding but different content structures. Her primary goal is to focus on writing clear technical explanations while automating the process of creating professional documentation portals.

## Key Requirements

1. **API Reference Generation**: Ability to extract code documentation (docstrings, type hints, function signatures) and convert it to navigable, searchable API references.
   - Critical for Sarah because it ensures documentation stays in sync with actual code and saves significant time compared to manually documenting APIs.
   - Must support popular documentation formats (e.g., Sphinx-style, Google-style, NumPy-style docstrings).

2. **Documentation Versioning**: Support for maintaining and displaying multiple versions of documentation corresponding to different software releases.
   - Essential for Sarah because users need access to documentation specific to the version they're using, while she needs to maintain updates across all supported versions.
   - Must include version selection UI metadata and proper URL structuring to separate versioned content.

3. **Code Snippet Highlighting**: Advanced syntax highlighting for code blocks with language detection, line numbering, and highlighting specific lines.
   - Important for Sarah because properly formatted code examples improve readability and comprehension in technical documentation.
   - Must support a wide range of programming languages with accurate syntax highlighting.

4. **Interactive Code Examples**: Ability to embed runnable code samples where readers can modify parameters and see results.
   - Valuable for Sarah because interactive examples help users understand API usage and experimentation without leaving the documentation.
   - Should support common languages used in examples with appropriate execution environments.

5. **Technical Diagram Generation**: Convert text-based diagram descriptions (e.g., Mermaid, PlantUML syntax) into visual diagrams.
   - Critical for Sarah because diagrams are essential for explaining complex systems, but maintaining them as images is cumbersome compared to text-based formats in version control.
   - Must generate high-quality, accessible diagram images from text descriptions.

## Technical Requirements

### Testability Requirements
- All components must be individually testable with clear interfaces
- Mock external systems (diagram renderers, code runners) for testing
- Support snapshot testing for generated HTML output
- Validate correct structure and cross-referencing in generated output
- Performance benchmarks should be established and tested for build times with large documentation sets

### Performance Expectations
- Must process 1000+ markdown files in under 60 seconds
- API extraction should handle libraries with 500+ functions/classes efficiently
- Incremental builds should complete in under 5 seconds for small changes
- Diagram generation should process 50+ diagrams in under 30 seconds
- Search index generation must be optimized for quick lookups even with large documentation sets

### Integration Points
- Code parsing tools for extracting API documentation from source code
- External diagram rendering services or libraries
- Version control systems for extracting versioning information
- Code execution environments for interactive examples
- Content distribution networks for optimized asset delivery
- Search indexing mechanisms

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must work with both local file systems and version control repositories as content sources
- Must generate static HTML that works without server-side processing
- Must guarantee content accuracy across versioned documentation
- Must ensure accessibility compliance in generated output
- Output should be optimized for both online viewing and PDF generation

## Core Functionality

The Technical Documentation Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **Content Processing Pipeline**
   - Parse and process Markdown and reStructuredText files
   - Extract metadata (title, description, version, etc.) from frontmatter
   - Apply transformations for diagrams, code blocks, and special syntax
   - Support for documentation-specific extensions and shortcodes

2. **API Documentation Extraction**
   - Parse Python source code to extract docstrings, type hints, and signatures
   - Generate structured API reference documentation from code
   - Maintain relationship between code and documentation for traceability
   - Support different docstring formats and styles

3. **Versioning System**
   - Track and manage multiple documentation versions
   - Generate version-specific output with appropriate navigation
   - Support for version aliases (latest, stable, etc.)
   - Maintain shared content across versions with version-specific overrides

4. **Interactive Components**
   - Transform code blocks with special syntax into interactive elements
   - Generate necessary assets for client-side code execution
   - Process and render technical diagrams from text descriptions
   - Create visualization helpers for API usage examples

5. **Site Generation and Structure**
   - Build consistent navigation structure from content hierarchy
   - Generate search indexes for client-side search functionality
   - Create sitemaps, redirects, and other navigation aids
   - Support for themes and customizable templates
   - Incremental build system that processes only changed files

## Testing Requirements

### Key Functionalities to Verify

1. **Content Transformation Accuracy**
   - Test conversion of various markup formats to HTML
   - Verify preservation of structure and formatting
   - Confirm proper generation of navigation elements
   - Validate cross-references and links

2. **API Documentation Extraction**
   - Test extraction from various Python codebases with different docstring styles
   - Verify accuracy of function signatures, parameters, and return types
   - Test handling of complex nested structures and inheritance
   - Confirm proper linking between related API elements

3. **Version Management**
   - Verify correct segregation of content by version
   - Test version selection mechanisms and redirects
   - Confirm proper handling of shared vs. version-specific content
   - Test upgrade and downgrade paths between versions

4. **Interactive Elements**
   - Test rendering of various diagram types from text descriptions
   - Verify generation of interactive code blocks
   - Test handling of different programming languages
   - Confirm accessibility of interactive elements

5. **Build Performance**
   - Benchmark build times for various repository sizes
   - Test incremental build performance
   - Verify memory usage stays within acceptable bounds
   - Test search index generation and query performance

### Critical User Scenarios

1. Adding a new version of documentation while maintaining older versions
2. Updating API documentation after code changes
3. Converting complex diagrams from text descriptions to visual format
4. Creating and testing interactive code examples
5. Performing targeted rebuilds after small content changes

### Performance Benchmarks

- Full builds of 1000+ pages should complete in under 60 seconds
- Incremental builds should complete in under 5 seconds for small changes
- Memory usage should not exceed 1GB for typical documentation repos
- Search indexing should process 100 pages/second
- API extraction should handle 10,000+ functions in under 30 seconds

### Edge Cases and Error Conditions

- Test handling of malformed markdown/reStructuredText
- Verify proper error reporting for invalid diagram syntax
- Test behavior with missing or corrupt source code for API docs
- Verify graceful degradation when interactive features can't be generated
- Test with extremely large files and deeply nested structures
- Validate handling of special characters and internationalization

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for API documentation extraction
- 100% coverage for version management logic
- Comprehensive integration tests for the entire build pipeline
- Performance tests must cover both small and large documentation sets

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

The Technical Documentation Site Generator will be considered successful if it:

1. Correctly extracts API documentation from Python source code and generates accurate, navigable references
2. Properly manages multiple versions of documentation with clear navigation between versions
3. Renders code snippets with correct syntax highlighting and line numbers
4. Successfully creates interactive code examples that can be modified and executed by users
5. Generates high-quality technical diagrams from text-based descriptions
6. Builds documentation sites efficiently, with proper incremental build support
7. Produces accessible, standards-compliant HTML output
8. Maintains consistent structure and styling across different documentation sections

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