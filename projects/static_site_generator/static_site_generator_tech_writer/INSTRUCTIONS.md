# Technical Documentation Site Generator

A specialized static site generator optimized for creating comprehensive technical documentation portals with consistent branding and flexible content structures.

## Overview

This project is a Python library for generating technical documentation websites from structured content files. It focuses on converting technical documentation into well-organized, searchable websites with features specifically designed for technical writers managing complex documentation across multiple software versions and products.

## Persona Description

Sarah creates comprehensive documentation for open-source software projects and needs to maintain multiple documentation sites with consistent branding but different content structures. Her primary goal is to focus on writing clear technical explanations while automating the process of creating professional documentation portals.

## Key Requirements

1. **API Reference Generation**: Transform code comments and docstrings into navigable API reference documentation. This feature is crucial for Sarah to ensure that developers can efficiently find function and class definitions without her manually maintaining separate API documentation that can drift out of sync with the code.

2. **Documentation Versioning**: Support multiple versions of documentation for different software releases within the same site structure. This allows Sarah to maintain documentation for legacy versions while continuing to update for new releases, ensuring users of all versions have access to appropriate documentation.

3. **Integrated Code Snippet Highlighting**: Provide syntax highlighting with language detection, line numbering, and copy functionality for code examples. Technical documentation requires extensive code samples, and proper formatting helps readers distinguish code from explanatory text and understand syntactical elements through color highlighting.

4. **Interactive Code Examples**: Embed runnable code samples where users can modify parameters and see results. This feature transforms passive documentation into an interactive learning experience, allowing readers to experiment with API usage patterns and better understand the behavior of documented components.

5. **Technical Diagram Generation**: Convert text-based diagram descriptions (like Mermaid or PlantUML syntax) into visual diagrams. Architectural and workflow diagrams are essential for technical documentation, and keeping them as text makes them version-controllable while automatically rendering them as images improves readability.

## Technical Requirements

- **Testability Requirements**:
  - All generation steps must be individually testable with discrete inputs and outputs
  - Diagram generation must validate input syntax and produce consistent output
  - API reference extraction must handle edge cases in code formatting and documentation styles
  - Versioning system must properly isolate and organize content for each version
  - All transformations from source to output must be deterministic and reproducible

- **Performance Expectations**:
  - Complete site generation for a 500-page documentation set should complete in under 5 minutes
  - Incremental builds should only process changed files and complete in under 30 seconds
  - Interactive examples must render and execute within 2 seconds of user modification
  - Large API references with 1000+ objects should render without pagination issues

- **Integration Points**:
  - Source code repositories for API reference extraction (local files or GitHub API)
  - Version control systems to extract versioning information
  - Diagram rendering engines (Mermaid, PlantUML, etc.)
  - Interactive code execution environments
  - Search indexing for documentation content

- **Key Constraints**:
  - All content processing must be possible without internet access for offline building
  - No server-side components for diagram rendering or code execution (client-side only)
  - Generated sites must be deployable as static files to any web server
  - Must support company-specific style guides and branding elements

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **Content Processing Pipeline**:
   - Parse multiple markup formats with custom extensions for technical content
   - Extract metadata for versioning, navigation, and categorization
   - Process special syntax for API references, code blocks, and diagrams
   - Apply templates for consistent rendering across content types

2. **Documentation Structure Management**:
   - Organize content hierarchically (sections, chapters, pages)
   - Handle cross-references between content pieces, including across versions
   - Generate navigation structures (sidebar, breadcrumbs, etc.)
   - Create indexes and table of contents for each documentation section

3. **Technical Content Enhancements**:
   - Extract and format API details from source code
   - Transform text-based diagram syntax into SVG or other visual formats
   - Implement syntax highlighting for multiple programming languages
   - Create interactive elements for code examples

4. **Publishing System**:
   - Generate static HTML, CSS, and JavaScript for all content
   - Bundle assets efficiently for deployment
   - Create verification tools to check for broken links and references
   - Support incremental rebuilds to minimize generation time

5. **Versioning Management**:
   - Track and organize multiple documentation versions
   - Generate version selectors and appropriate navigation
   - Maintain URL structures that include version information
   - Support deprecation notices and version compatibility notes

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate API reference generation from various code styles and documentation formats
  - Proper versioning of content with correct relationships between versions
  - Functional code snippet highlighting with language detection and formatting
  - Successful rendering of diagrams from text specifications
  - Working interactive code examples with proper execution

- **Critical User Scenarios**:
  - Documentation writer adds new version with updates to existing content
  - Technical content includes complex nested structures (lists within code blocks, etc.)
  - API reference generation from incomplete or inconsistently formatted code
  - Handling of special characters and symbols in technical documentation
  - Cross-referencing between different documentation sections and versions

- **Performance Benchmarks**:
  - Full build time for documentation sets of various sizes (100, 500, 1000 pages)
  - Incremental build time when changing different content types
  - Load and execution time for interactive code examples
  - Memory usage during build process for large documentation sets

- **Edge Cases and Error Conditions**:
  - Malformed markup or syntax in source content
  - Invalid or unparseable diagram specifications
  - Missing code references for API documentation
  - Circular references in documentation structure
  - Version conflicts or overlapping version specifications

- **Required Test Coverage**:
  - 95% code coverage for core library functions
  - 100% coverage for API reference extraction logic
  - 100% coverage for versioning management features
  - Comprehensive tests for all supported markup formats and extensions

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. A technical writer can convert a repository of Markdown and reStructuredText files into a fully featured documentation site without manual HTML editing
2. API reference documentation stays synchronized with source code through automated extraction
3. Multiple documentation versions can coexist with clear navigation between them
4. Code examples are properly highlighted and interactive examples work in a static environment
5. Text-based diagram specifications are correctly rendered as visual diagrams
6. The complete build process for a 500-page documentation set completes in under 5 minutes
7. All tests pass with at least 95% code coverage
8. The generated site can be deployed to any static hosting service without additional processing

To set up your development environment:
```
uv venv
source .venv/bin/activate
```