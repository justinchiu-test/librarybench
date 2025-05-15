# Server Management Workflow Automation Engine

## Overview
A specialized workflow automation engine designed for system administrators, enabling secure remote execution, controlled progressive deployments, scheduled maintenance operations, configuration verification, and optimized parallel task execution. This system provides reliable automation for server management tasks across multiple data centers without requiring additional agent installations.

## Persona Description
Miguel manages hundreds of servers across multiple data centers and needs to automate routine maintenance, updates, and troubleshooting procedures. He requires reliable automation that can work with existing systems without installing agents.

## Key Requirements
1. **SSH-Based Execution**: Implement secure command execution on remote systems without additional agents. This feature is critical for Miguel because his organization restricts the installation of third-party agents on production servers, yet he still needs to perform consistent, automated operations across a large server fleet.

2. **Progressive Execution**: Create a system for applying changes to server groups in controlled waves. Miguel requires this capability because making changes to all servers simultaneously is too risky; he needs to verify successful changes on a small subset of servers before proceeding to the next group, reducing the blast radius of potential issues.

3. **Maintenance Window Scheduling**: Develop coordination of tasks during approved change periods. This feature is vital for Miguel as his organization enforces strict change management policies that restrict when certain systems can be modified, requiring automated tasks to execute within specific approved time windows.

4. **Configuration Verification**: Implement system state comparison before and after changes. Miguel needs this functionality because he must validate that server configurations have been correctly applied and that systems are in the expected state after automated changes to ensure service reliability and compliance.

5. **Parallel Execution Optimization**: Build maximized efficiency while respecting system constraints. This capability is essential for Miguel because managing hundreds of servers requires efficient parallelization to complete maintenance tasks within limited maintenance windows, but must be balanced against resource constraints to prevent overloading networks or shared infrastructure.

## Technical Requirements
- **Testability Requirements**:
  - SSH execution must be testable without requiring actual remote servers
  - Progressive execution logic must be verifiable through simulated server groups
  - Maintenance window scheduling must be testable with time manipulation
  - Configuration verification must be testable with mock system states
  - Parallel execution strategies must be testable with simulated operation durations

- **Performance Expectations**:
  - SSH connection pooling should maintain at least 100 concurrent connections
  - Progressive execution should support configurations for at least 10 server groups
  - Scheduling system should handle at least 1,000 maintenance windows
  - Configuration verification should process server state checks at 50+ per minute
  - Parallel execution should optimize for at least 200 concurrent operations while respecting constraints

- **Integration Points**:
  - SSH and other remote execution protocols (WinRM, etc.)
  - Server inventory and configuration management databases
  - Change management and approval systems
  - Monitoring systems for server state information
  - Notification systems for status updates and alerts
  - Logging and auditing systems for compliance documentation

- **Key Constraints**:
  - All functionality must be implemented as libraries and APIs, not as applications with UIs
  - System must operate with minimal resource footprint
  - Must work in environments with varying network reliability
  - Must respect rate limits for various infrastructure components
  - Must handle credential management securely without storing sensitive information
  - Must operate in network-segmented environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Server Management Workflow Automation Engine centers around secure, controlled server operations:

1. **Workflow Definition System**: A Python API and YAML/JSON parser for defining server management workflows with progressive execution, scheduling constraints, and verification steps.

2. **Secure Remote Execution**: Components for establishing secure connections to remote systems, executing commands, and safely handling command output with proper error management.

3. **Server Group Manager**: Modules that organize servers into logical groups for progressive execution, with configurable promotion criteria between waves.

4. **Maintenance Window Scheduler**: A scheduling system that understands maintenance window constraints and ensures operations execute only during approved periods.

5. **Configuration Verification Framework**: Components that capture system state before changes, define expected states after changes, and verify actual results match expectations.

6. **Parallel Execution Controller**: A system that optimizes task parallelization based on server groups, resource constraints, and system dependencies.

7. **Execution Engine**: The core orchestrator that manages workflow execution, handles task dependencies, and coordinates the various components while maintaining workflow state.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Secure and reliable remote command execution
  - Proper implementation of progressive execution across server groups
  - Accurate scheduling within maintenance windows
  - Thorough configuration verification before and after changes
  - Efficient parallel execution with appropriate constraint handling

- **Critical User Scenarios**:
  - Multi-stage server patching across different data centers
  - Configuration deployment with progressive rollout
  - Complex maintenance procedure during restricted time windows
  - Recovery procedures when changes fail verification
  - Cross-platform operations on heterogeneous server environments
  - Large-scale parallel operations with resource constraint handling

- **Performance Benchmarks**:
  - Maintain 100+ concurrent SSH connections
  - Process 50+ configuration verifications per minute
  - Support 200+ concurrent operations within resource constraints
  - Handle 1,000+ scheduled maintenance windows
  - Execute operations on 1,000+ servers within a 4-hour maintenance window

- **Edge Cases and Error Conditions**:
  - Network partitions during operations
  - Partial failures within server groups
  - Maintenance window expiration during execution
  - Unexpected server state differences
  - Credential rotation during long-running operations
  - Resource exhaustion on target systems
  - SSH connection limits and timeouts
  - Conflicting change requests

- **Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for SSH execution and security handling
  - 100% coverage for progressive execution logic
  - 100% coverage for configuration verification
  - All error handling paths must be tested

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
A successful implementation of the Server Management Workflow Automation Engine will meet the following criteria:

1. Secure remote execution system that correctly executes commands on remote systems without requiring agent installation, verified through tests with simulated SSH endpoints.

2. Progressive execution that properly applies changes to server groups in waves with appropriate validation between stages, confirmed through tests with various server grouping scenarios.

3. Maintenance window scheduling that ensures operations execute only during approved periods, demonstrated by tests with various time-based constraints.

4. Configuration verification that accurately detects discrepancies between expected and actual server states, validated through systematic testing with various configuration scenarios.

5. Parallel execution optimization that maximizes throughput while respecting resource constraints, measured through performance testing with simulated operations.

6. Performance meeting or exceeding the specified benchmarks for connection pooling, processing rates, and scalability.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Project Setup Instructions
To set up the development environment:

1. Create a virtual environment:
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

4. Install test dependencies:
   ```
   pip install pytest pytest-json-report
   ```

CRITICAL REMINDER: It is MANDATORY to run the tests with pytest-json-report and provide the pytest_results.json file as proof of successful implementation:
```
pytest --json-report --json-report-file=pytest_results.json
```