# PyMockAPI - Demo Presentation Mock Server

## Overview
A specialized HTTP API mock server designed for solutions engineers to create polished, realistic demonstrations without complex setup or real data dependencies. This implementation focuses on generating beautiful, industry-specific mock data with scripted scenarios that create impressive, believable product demonstrations.

## Persona Description
A solutions engineer creating product demonstrations who needs polished, realistic mock data for presentations. She wants to quickly create impressive demos without complex setup or real data dependencies.

## Key Requirements

1. **Industry-specific data generators (finance, healthcare, retail)**
   - Essential for creating believable demonstrations for different verticals
   - Enables realistic data that resonates with specific audience segments

2. **Persona-based data consistency across endpoints**
   - Critical for maintaining narrative coherence throughout demonstrations
   - Ensures that data relationships remain logical and believable

3. **Demo scenario scripting with timed progressions**
   - Vital for creating dynamic, engaging demonstrations
   - Allows for storytelling through data progression

4. **Beautiful response data with Lorem Ipsum alternatives**
   - Required for visually appealing demonstrations
   - Ensures data looks professional and polished

5. **Screen recording integration with annotation support**
   - Essential for creating reusable demo assets
   - Enables post-production enhancement of demonstrations

## Technical Requirements

### Testability Requirements
- All data generators must produce consistent, predictable output
- Scenario scripts must execute deterministically
- Industry data must be validatable for accuracy
- Recording triggers must be programmable

### Performance Expectations
- Data generation within 50ms for any request
- Scenario state transitions within 100ms
- Support for 10+ concurrent demo sessions
- No performance degradation during recording

### Integration Points
- RESTful API for demo configuration
- WebSocket API for scenario progression
- Export APIs for generated data sets
- Recording trigger and annotation APIs

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Generated data must be legally compliant (no real PII)
- Should produce visually appealing JSON/XML responses

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Industry Data Generators**: Sophisticated generators for multiple industries including realistic company names, financial data, healthcare records (HIPAA-compliant fake data), retail transactions, and industry-specific terminology.

2. **Persona Consistency Engine**: System maintaining data relationships across API calls, ensuring that customer profiles, transaction histories, and related data remain consistent throughout demo sessions.

3. **Scenario Script Runner**: Time-based scenario execution system with support for data progression, state changes, event triggers, and narrative waypoints.

4. **Beautiful Data Formatter**: Response beautification system that generates visually appealing data with proper formatting, realistic names and addresses, meaningful descriptions, and coherent relationships.

5. **Demo Recorder Integration**: Hooks for screen recording tools with annotation triggers, scenario markers, timing synchronization, and export capabilities.

## Testing Requirements

### Key Functionalities to Verify
- Industry data generators produce realistic, valid data
- Persona consistency is maintained across all endpoints
- Scenario scripts execute with proper timing
- Generated data is visually appealing and coherent
- Recording integration triggers work correctly

### Critical User Scenarios
- Running a complete product demo for healthcare clients
- Demonstrating financial analytics with realistic data
- Showing retail customer journey with consistent personas
- Creating timed progression demos for sales pitches
- Recording and annotating demo sessions

### Performance Benchmarks
- Generate any response within 50ms
- Transition scenario states within 100ms
- Support 10+ concurrent demo sessions
- Maintain 60fps during recording operations
- Handle 1000+ requests per demo session

### Edge Cases and Error Conditions
- Handling requests for non-existent personas
- Scenario script timing conflicts
- Data generation for edge case industries
- Recording triggers during high load
- Maintaining consistency across session restarts

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for data generators
- Industry data validation tests
- Scenario timing accuracy tests
- Integration tests for recording hooks

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

1. Industry-specific data is realistic and compelling
2. Demo narratives remain consistent throughout sessions
3. Scenario progressions create engaging demonstrations
4. Generated data is visually impressive
5. Recording integration enhances demo creation workflow

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
4. Showing compelling demo scenarios with beautiful data

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.