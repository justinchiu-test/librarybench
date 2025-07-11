# PyMockAPI - Contract-Driven Mock Server

## Overview
A specialized HTTP API mock server designed for API contract developers to validate API designs through accurate mock implementations. This implementation focuses on maintaining strict alignment between mock behaviors and API specifications, enabling contract-first development with comprehensive validation and documentation generation.

## Persona Description
A backend developer designing API contracts who uses mocks to validate API designs before implementation. He needs to ensure mocks accurately reflect the planned API specification and can generate documentation.

## Key Requirements

1. **OpenAPI specification synchronization with bidirectional updates**
   - Essential for keeping mocks and specifications in perfect alignment
   - Enables automatic mock generation from specs and spec updates from mock changes

2. **Contract validation mode with strict schema enforcement**
   - Critical for ensuring all mock responses comply with defined contracts
   - Prevents drift between mock behavior and actual API specifications

3. **API documentation generation from mock definitions**
   - Vital for maintaining up-to-date, accurate API documentation
   - Enables stakeholders to understand API behavior through mock examples

4. **Breaking change detection between mock versions**
   - Required for identifying backward compatibility issues early
   - Ensures API evolution doesn't break existing consumers

5. **Mock-driven API design workflow with approval process**
   - Essential for validating API designs through working mocks before implementation
   - Enables stakeholder review and approval of API behavior

## Technical Requirements

### Testability Requirements
- All contract validation must be programmable and testable
- OpenAPI synchronization must support automated testing
- Documentation generation must produce consistent outputs
- Breaking change detection must be deterministic

### Performance Expectations
- OpenAPI spec parsing and validation under 1 second
- Contract validation on each request under 50ms
- Documentation generation under 5 seconds
- Breaking change analysis under 2 seconds

### Integration Points
- OpenAPI 3.0+ specification support
- JSON Schema validation engine
- API for retrieving generated documentation
- Contract comparison and diff APIs

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must support standard OpenAPI specifications
- Should generate documentation in common formats (Markdown, HTML)

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **OpenAPI Synchronization Engine**: Bidirectional synchronization between OpenAPI specifications and mock configurations, supporting both mock generation from specs and spec updates from mocks.

2. **Contract Validation System**: Strict request and response validation against OpenAPI schemas, with detailed error reporting for contract violations.

3. **Documentation Generator**: Automatic generation of comprehensive API documentation from mock definitions, including request/response examples and error scenarios.

4. **Breaking Change Analyzer**: Comparison engine that detects breaking changes between different versions of API contracts, including removed endpoints, changed schemas, and modified behaviors.

5. **Design Workflow Manager**: Support for mock-driven API design with draft/review/approved states, version tracking, and stakeholder approval mechanisms.

## Testing Requirements

### Key Functionalities to Verify
- OpenAPI synchronization maintains specification accuracy
- Contract validation correctly identifies schema violations
- Documentation generation produces accurate, complete output
- Breaking change detection identifies all compatibility issues
- Workflow states transition correctly with approvals

### Critical User Scenarios
- Importing OpenAPI spec and generating mocks automatically
- Validating mock responses against strict schemas
- Generating documentation for API review meetings
- Detecting breaking changes before deployment
- Managing API design approval workflows

### Performance Benchmarks
- OpenAPI parsing/validation under 1 second
- Per-request validation under 50ms
- Documentation generation under 5 seconds
- Breaking change analysis under 2 seconds
- Support for specs with 100+ endpoints

### Edge Cases and Error Conditions
- Handling invalid or incomplete OpenAPI specifications
- Circular references in schema definitions
- Contract violations with detailed error context
- Version comparison with major structural changes
- Approval workflow with rejected designs

### Required Test Coverage
- Minimum 95% code coverage for all core modules
- 100% coverage for contract validation logic
- Integration tests for OpenAPI compatibility
- End-to-end tests for complete workflows
- Regression tests for specification edge cases

**IMPORTANT**:
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

The implementation will be considered successful when:

1. Mocks and OpenAPI specifications remain perfectly synchronized
2. Contract violations are caught and reported clearly
3. Generated documentation accurately reflects API behavior
4. Breaking changes are detected reliably
5. API design workflow supports effective collaboration

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:
1. Create a virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in editable mode with `uv pip install -e .`
4. Install test dependencies including pytest-json-report

## Validation

The final implementation must be validated by:
1. Running all tests with pytest-json-report
2. Generating and providing the pytest_results.json file
3. Demonstrating all five key requirements are fully implemented
4. Showing successful contract-driven development workflow

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.