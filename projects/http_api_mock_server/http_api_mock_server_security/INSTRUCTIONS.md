# PyMockAPI - Security Testing Mock Server

## Overview
A specialized HTTP API mock server designed for security analysts to test application resilience against various attack scenarios and malformed responses. This implementation focuses on simulating security vulnerabilities, attack patterns, and edge cases to ensure applications handle malicious inputs and unexpected responses securely.

## Persona Description
A security analyst testing application resilience who needs to simulate various attack scenarios and malformed responses. He wants to ensure applications handle malicious inputs and unexpected responses securely.

## Key Requirements

1. **Malformed response injection with fuzzing capabilities**
   - Essential for testing application parsing and error handling robustness
   - Enables discovery of injection vulnerabilities and buffer overflows

2. **Authentication bypass scenarios for security testing**
   - Critical for validating authentication and authorization implementations
   - Allows testing of privilege escalation and access control weaknesses

3. **Rate limiting simulation with custom denial responses**
   - Vital for testing application behavior under rate limiting and DDoS scenarios
   - Enables validation of graceful degradation and user messaging

4. **CORS policy testing with various origin configurations**
   - Required for validating cross-origin security implementations
   - Ensures proper handling of preflight requests and origin validation

5. **Security header manipulation for vulnerability assessment**
   - Essential for testing application response to missing or malicious headers
   - Enables validation of security header enforcement and CSP policies

## Technical Requirements

### Testability Requirements
- All security scenarios must be configurable and reproducible
- Fuzzing must support deterministic and random modes
- Authentication scenarios must be scriptable
- Security violations must be detectable and measurable

### Performance Expectations
- Fuzzing operations must generate 100+ variations per second
- Support for concurrent attack scenario execution
- Response manipulation with minimal latency overhead (<10ms)
- Real-time security event logging and analysis

### Integration Points
- API for configuring security test scenarios
- Fuzzing engine with customizable generators
- Security event logging and alerting APIs
- Integration with security scanning tools

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must not introduce actual vulnerabilities
- Should safely simulate attacks without system compromise

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Response Fuzzer**: Advanced fuzzing engine capable of generating malformed responses including invalid JSON, XML injection, oversized payloads, and encoding attacks.

2. **Authentication Simulator**: Configurable authentication bypass scenarios including token manipulation, session hijacking, privilege escalation, and JWT vulnerabilities.

3. **Rate Limit Engine**: Sophisticated rate limiting with various algorithms (token bucket, sliding window) and customizable denial responses including retry headers.

4. **CORS Policy Manager**: Comprehensive CORS testing with configurable policies, preflight handling, credential scenarios, and wildcard origin testing.

5. **Security Header Controller**: Dynamic manipulation of security headers including CSP, HSTS, X-Frame-Options, with violation reporting and policy testing.

## Testing Requirements

### Key Functionalities to Verify
- Fuzzing generates appropriate malformed responses
- Authentication bypasses work as configured
- Rate limiting enforces limits accurately
- CORS policies are applied correctly
- Security headers are manipulated as specified

### Critical User Scenarios
- Testing application response to malformed JSON/XML
- Validating authentication bypass prevention
- Confirming rate limit handling and recovery
- Verifying CORS policy enforcement
- Testing security header compliance

### Performance Benchmarks
- Generate 100+ fuzzed responses per second
- Support 50+ concurrent security scenarios
- Response manipulation latency under 10ms
- Security event logging without performance impact
- Handle 1000+ requests while under attack simulation

### Edge Cases and Error Conditions
- Handling of extremely large malformed payloads
- Recovery from authentication system overload
- Rate limit edge cases (boundary conditions)
- CORS preflight request edge cases
- Conflicting security header directives

### Required Test Coverage
- Minimum 95% code coverage for all core modules
- 100% coverage for security-critical paths
- Fuzzing test coverage for all input types
- Integration tests for all attack scenarios
- Regression tests for discovered vulnerabilities

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

1. Security testing scenarios accurately simulate real attacks
2. Applications can be thoroughly tested for security weaknesses
3. Fuzzing discovers potential vulnerability patterns
4. Authentication and authorization can be comprehensively tested
5. Security headers and policies are validated effectively

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
4. Showing effective security testing capabilities

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.