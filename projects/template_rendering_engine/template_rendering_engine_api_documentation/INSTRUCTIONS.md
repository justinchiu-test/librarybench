# PyTemplate for API Documentation Generation

## Overview
A specialized template rendering engine for generating comprehensive API documentation from OpenAPI specifications, supporting multiple output formats and interactive examples for technical writers and documentation teams.

## Persona Description
A technical writer maintaining API documentation who needs to generate consistent documentation from OpenAPI specifications. She requires templates that can handle complex data structures and produce multiple output formats.

## Key Requirements
1. **OpenAPI/Swagger data structure traversal helpers**: The engine must provide powerful helpers to navigate complex OpenAPI specifications, including nested schemas, references, and polymorphic types. This is critical for accurately documenting APIs with hundreds of endpoints and complex data models.

2. **Multi-format output (HTML, PDF, Markdown) from one template**: Single-source templates must generate documentation in multiple formats without modification, ensuring consistency across different documentation channels while maintaining format-specific optimizations.

3. **Interactive API example generation with curl/code snippets**: Automatically generate working code examples in multiple programming languages (curl, Python, JavaScript, etc.) from OpenAPI definitions, essential for developers who need quick implementation references.

4. **Version comparison with change highlighting**: Built-in diff capabilities to compare API versions and highlight breaking changes, additions, and deprecations. This is crucial for helping API consumers understand version migration requirements.

5. **Search index generation for documentation sites**: Automatically generate search indices compatible with popular documentation search engines (Algolia, ElasticSearch), enabling users to quickly find specific API endpoints and concepts.

## Technical Requirements
- **Testability**: All OpenAPI parsing and documentation generation logic must be thoroughly testable with pytest
- **Performance**: Must handle large OpenAPI specifications (1000+ endpoints) efficiently
- **Integration**: Clean API for integration with documentation platforms and CI/CD pipelines
- **Key Constraints**: No UI components; must support OpenAPI 3.0+ and Swagger 2.0; handle circular references gracefully

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- OpenAPI specification parser with reference resolution and circular reference handling
- Template helpers for common API documentation patterns (endpoint lists, schema tables, etc.)
- Multi-format renderer supporting HTML, PDF (via intermediate format), and Markdown
- Code example generator for multiple languages with syntax highlighting support
- Version diff engine that identifies and categorizes API changes
- Search index builder with customizable field extraction
- Response/request example generator from schemas
- Authentication documentation generator for various auth schemes

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **OpenAPI parsing tests**: Verify correct handling of complex specifications with references
- **Format generation tests**: Validate output in HTML, Markdown, and PDF-ready formats
- **Code example tests**: Ensure generated examples are syntactically correct and runnable
- **Version diff tests**: Validate accurate detection of API changes between versions
- **Search index tests**: Verify correct extraction and indexing of documentation content
- **Performance tests**: Benchmark processing of large API specifications
- **Edge cases**: Handle malformed specs, circular references, missing schemas
- **Compatibility tests**: Ensure support for both OpenAPI 3.0+ and Swagger 2.0

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
- Correctly parses and documents complex OpenAPI specifications with 500+ endpoints
- Generates consistent documentation across HTML, PDF, and Markdown formats
- Produces working code examples that can be copy-pasted and executed
- Accurately identifies all breaking changes between API versions
- Creates search indices that enable sub-second search across large API docs
- Handles circular references and complex schema inheritance properly
- All tests pass with comprehensive API coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file