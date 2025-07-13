# PyTemplate for Static Site Generation

## Overview
A specialized template rendering engine designed for static site generators, focusing on advanced markdown integration, code syntax highlighting, and efficient static HTML generation for technical blogs and documentation sites.

## Persona Description
A developer building a static site generator for technical blogs who needs advanced markdown integration and code syntax highlighting. She requires a template engine that can handle complex content transformations and generate optimized static HTML.

## Key Requirements
1. **Markdown parsing with custom extension support in templates**: The engine must seamlessly integrate markdown content within templates, supporting custom markdown extensions like footnotes, tables, and custom containers. This is critical for technical bloggers who need rich content formatting beyond standard markdown.

2. **Syntax highlighting with language detection and theming**: Code blocks must be automatically highlighted with support for multiple programming languages and customizable color themes. This feature is essential for technical blogs where code examples are a primary content type.

3. **Static asset fingerprinting and optimization pipeline**: The system must generate unique fingerprints for static assets (CSS, JS, images) to enable aggressive caching and include an optimization pipeline for minification and compression. This ensures optimal performance for static sites.

4. **RSS/Atom feed generation from template data**: Templates must support generating standards-compliant RSS and Atom feeds directly from content data, crucial for blog readers and content syndication.

5. **Incremental regeneration based on content changes**: The engine must track dependencies and only regenerate affected pages when content changes, significantly improving build times for large sites with thousands of pages.

## Technical Requirements
- **Testability**: All functionality must be exposed through a Python API that can be thoroughly tested with pytest, including mock filesystem operations and performance benchmarks
- **Performance**: Template compilation and rendering must be optimized for bulk operations, with the ability to process hundreds of templates in parallel
- **Integration**: Clean API for integration with markdown processors, syntax highlighters, and asset pipeline tools
- **Key Constraints**: No UI components - all functionality must be library-based; must handle large numbers of templates efficiently; thread-safe for parallel processing

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- A markdown-aware template parser that can handle markdown content blocks within templates
- Integration points for syntax highlighting libraries with theme support
- Asset management system with fingerprinting and URL rewriting capabilities
- Feed generation templates with automatic content extraction and formatting
- Dependency tracking system that maps template relationships for incremental builds
- Template compilation with optimizations for static site generation patterns
- Context processors for common static site data (navigation, metadata, etc.)

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **Markdown integration tests**: Verify correct parsing and rendering of various markdown extensions
- **Syntax highlighting tests**: Validate language detection and theme application for different code blocks
- **Asset pipeline tests**: Ensure correct fingerprinting, URL rewriting, and optimization
- **Feed generation tests**: Validate RSS/Atom compliance and content extraction
- **Incremental build tests**: Verify dependency tracking and selective regeneration
- **Performance benchmarks**: Test rendering speed for sites with 1000+ pages
- **Edge cases**: Handle malformed markdown, missing assets, circular dependencies
- **Thread safety tests**: Verify parallel rendering doesn't cause race conditions

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
The implementation is successful when:
- All markdown content renders correctly with custom extensions
- Code syntax highlighting works for at least 20 common languages
- Asset fingerprinting reduces page load times by enabling aggressive caching
- RSS/Atom feeds validate against W3C standards
- Incremental builds reduce regeneration time by at least 80% for single-page changes
- Full site generation handles 1000+ pages in under 30 seconds
- All tests pass with 100% coverage of public APIs

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file