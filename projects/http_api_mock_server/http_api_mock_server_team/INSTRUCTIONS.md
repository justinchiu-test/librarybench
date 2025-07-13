# PyMockAPI - Team Collaboration Mock Server

## Overview
A specialized HTTP API mock server designed for frontend team leads to manage and share mock configurations across distributed development teams. This implementation focuses on centralized mock management, team collaboration features, and configuration consistency while allowing individual developers the flexibility to create custom scenarios.

## Persona Description
A team lead coordinating multiple frontend developers who needs to share mock configurations across the team. She wants centralized mock management to ensure consistency while allowing individual developers to create custom scenarios.

## Key Requirements

1. **Git-based mock configuration sharing with merge conflict resolution**
   - Critical for version-controlled mock definitions that integrate with existing workflows
   - Enables team members to collaborate on mock configurations using familiar tools

2. **Team workspace management with role-based permissions**
   - Essential for organizing mocks by project, feature, or team with appropriate access controls
   - Ensures sensitive mock data is only accessible to authorized team members

3. **Mock inheritance hierarchy for base/override patterns**
   - Vital for maintaining consistent base behaviors while allowing customization
   - Reduces duplication and ensures updates propagate correctly

4. **Real-time collaboration with WebSocket-based updates**
   - Required for immediate visibility when team members modify shared mocks
   - Enables live debugging sessions and pair programming scenarios

5. **Mock versioning with environment-specific deployments**
   - Critical for maintaining different mock configurations across dev/staging/prod
   - Allows safe experimentation without affecting other environments

## Technical Requirements

### Testability Requirements
- All collaboration features must be testable via Python APIs
- Git operations must be mockable for testing without actual repositories
- WebSocket connections must support automated testing
- Permission system must be fully testable with various role scenarios

### Performance Expectations
- Mock configuration changes must propagate within 1 second
- Support for at least 20 concurrent team members
- Git operations must complete within 5 seconds
- WebSocket message delivery under 100ms latency

### Integration Points
- Git integration for configuration storage and versioning
- RESTful API for workspace and permission management
- WebSocket API for real-time updates
- Export/import APIs for configuration portability

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must work with standard Git implementations
- Should not require external collaboration tools

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Git Integration Layer**: A system that stores mock configurations in Git repositories, handles commits, merges, and conflict resolution for mock definition files.

2. **Workspace Management System**: Multi-tenant workspace support with project-based organization, team member management, and role-based access control.

3. **Configuration Inheritance Engine**: A hierarchical system where base mock configurations can be extended and overridden at various levels (global, project, feature, developer).

4. **Real-time Collaboration Protocol**: WebSocket-based system for broadcasting configuration changes, active user presence, and collaborative editing notifications.

5. **Environment Version Manager**: A system for tagging, deploying, and managing different versions of mock configurations across multiple environments.

## Testing Requirements

### Key Functionalities to Verify
- Git operations correctly version and merge mock configurations
- Role-based permissions properly restrict access
- Inheritance hierarchy resolves overrides correctly
- WebSocket updates deliver to all connected clients
- Environment deployments maintain version integrity

### Critical User Scenarios
- Multiple developers modifying the same mock configuration
- Resolving conflicts when merging feature branches
- Inheriting and overriding base mock behaviors
- Real-time updates during collaborative debugging
- Deploying specific versions to different environments

### Performance Benchmarks
- Configuration change propagation under 1 second
- Support for 20+ concurrent users
- Git operations complete within 5 seconds
- WebSocket latency under 100ms
- No degradation with 1000+ mock definitions

### Edge Cases and Error Conditions
- Handling Git merge conflicts in mock configurations
- Recovery from network partitions during collaboration
- Permission changes while users are active
- Circular dependencies in inheritance hierarchies
- WebSocket reconnection with message recovery

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for permission and security logic
- Integration tests for Git operations
- Concurrency tests for real-time features
- End-to-end tests for complete workflows

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

1. Teams can effectively share and version mock configurations
2. Role-based permissions provide appropriate access control
3. Configuration inheritance reduces duplication and maintenance
4. Real-time collaboration features work reliably
5. Environment-specific deployments are manageable and traceable

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
4. Showing successful team collaboration scenarios

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.