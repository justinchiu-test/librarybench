# PyTemplate for Microservices Code Generation

## Overview
A specialized template rendering engine for generating consistent microservice boilerplate code, API contracts, and service mesh configurations, enabling architects to maintain standards across distributed systems.

## Persona Description
An architect generating boilerplate code for microservices who needs templates for different service patterns. He wants to maintain consistency across services while allowing customization for specific requirements.

## Key Requirements
1. **Service scaffold generation with dependency injection**: Generate complete service skeletons including dependency injection setup, health checks, and standard middleware. This is critical for ensuring all services follow architectural patterns and best practices from the start.

2. **API contract code generation from specifications**: Transform API specifications (OpenAPI, gRPC proto) into client SDKs, server stubs, and validation logic. This ensures type-safe communication between services and reduces integration errors.

3. **Middleware and interceptor pattern templates**: Create reusable middleware components for cross-cutting concerns (authentication, logging, tracing) that can be consistently applied across services. This is essential for maintaining operational standards in distributed systems.

4. **Service mesh configuration generation**: Generate Istio, Linkerd, or similar service mesh configurations including routing rules, circuit breakers, and security policies. This enables consistent network behavior and observability across the microservices ecosystem.

5. **Multi-language code generation support**: Support generating code in multiple languages (Python, Go, Java, TypeScript) from the same template definitions. This is crucial for polyglot microservices architectures where different services use different technology stacks.

## Technical Requirements
- **Testability**: All code generation logic must be testable via pytest with validation of generated code syntax
- **Performance**: Must generate complete service scaffolds in seconds, not minutes
- **Integration**: Clean API for integration with CI/CD pipelines and development workflows
- **Key Constraints**: No UI components; generated code must be production-ready; support for modern microservice patterns

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- Service scaffold generator with configurable patterns (REST, gRPC, event-driven)
- API specification parser supporting OpenAPI 3.0 and Protocol Buffers
- Code generator with language-specific templates and idioms
- Middleware template system with composition capabilities
- Service mesh config generator for major platforms
- Dependency injection container setup for different frameworks
- Project structure generator with build configurations
- Documentation generator for service interfaces

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **Scaffold generation tests**: Verify complete, runnable service code generation
- **API contract tests**: Validate generated code matches specifications exactly
- **Middleware tests**: Ensure generated middleware follows correct patterns
- **Service mesh tests**: Verify configuration validity for target platforms
- **Multi-language tests**: Validate syntax and idioms for each target language
- **Integration tests**: Ensure generated services can communicate properly
- **Performance tests**: Benchmark generation time for complex services
- **Code quality tests**: Verify generated code passes linters and type checkers

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
- Generated service scaffolds compile/run without modification
- API contracts produce type-safe client/server code
- Middleware components integrate seamlessly with service frameworks
- Service mesh configurations deploy without errors
- Multi-language output follows language-specific best practices
- Complex microservice (50+ endpoints) generates in under 10 seconds
- Generated code passes all relevant linters and security scanners
- All tests pass with validation of generated code quality

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file