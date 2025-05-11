# Operationally Resilient Microservices Framework

## Overview
This project is a specialized event-driven microservices framework designed for DevOps environments that prioritizes operational reliability, automated recovery, and comprehensive observability. It provides service health monitoring, zero-downtime deployment capabilities, chaos testing integration, dynamic resource scaling, and comprehensive tracing to create a robust microservices platform that minimizes operational overhead.

## Persona Description
Alex manages infrastructure for a rapidly growing startup that needs to scale services quickly without compromising reliability. His primary goal is to implement a microservices platform with robust operational characteristics that supports automated deployment, monitoring, and recovery to minimize operational overhead.

## Key Requirements

1. **Service Health Monitoring with Automated Recovery Mechanisms**
   - Implement comprehensive health checking for all services
   - Create automated recovery procedures for common failure patterns
   - Support for dependency-aware health evaluation and recovery sequencing
   - Include degraded operation detection and remediation
   - This feature is critical for minimizing operational overhead by enabling self-healing systems that recover automatically from failures

2. **Deployment Orchestration with Zero-downtime Updates**
   - Develop rolling update strategies with traffic shifting
   - Create blue/green deployment patterns for microservices
   - Support for automatic rollback on deployment failures
   - Include deployment verification through health metrics
   - This feature ensures continuous service availability during updates and minimizes deployment risk

3. **Chaos Testing Integration for Resilience Verification**
   - Implement controllable fault injection across the microservices ecosystem
   - Create scenario-based resilience testing
   - Support for automated resilience verification
   - Include chaos experiment reporting and documentation
   - This feature proactively validates system resilience by intentionally introducing failures to ensure recovery mechanisms function correctly

4. **Resource Utilization Optimization with Dynamic Scaling**
   - Develop automated scaling based on service demand metrics
   - Create resource utilization monitoring and forecasting
   - Support for cost-optimization through intelligent resource allocation
   - Include capacity planning tools for growth projections
   - This feature optimizes infrastructure costs while ensuring sufficient capacity for variable workloads

5. **Comprehensive Tracing and Logging Infrastructure**
   - Implement distributed tracing across service boundaries
   - Create structured logging with correlation identifiers
   - Support for centralized log aggregation and analysis
   - Include performance metrics collection and visualization
   - This feature provides complete visibility into system behavior for troubleshooting and optimization

## Technical Requirements

### Testability Requirements
- Support for automated resilience testing
- Ability to simulate various failure scenarios
- Testing of deployment and rollback procedures
- Verification of monitoring and recovery mechanisms

### Performance Expectations
- Support for at least 1,000 service instances
- Maximum 30-second recovery time for failed services
- Ability to handle 100+ deployments per day without service disruption
- Support for comprehensive tracing across 10,000+ transactions per second

### Integration Points
- Integration with container orchestration platforms (conceptual, no actual K8s dependency)
- Support for infrastructure as code principles
- Compatibility with popular monitoring and observability tools
- Integration with CI/CD pipelines for automated deployment

### Key Constraints
- Must operate without service disruption during maintenance
- Must scale horizontally for both the framework and managed services
- Must provide comprehensive operational visibility
- Must minimize human intervention for routine operational tasks

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Health Monitoring and Recovery System**
   - Service health checks and monitoring
   - Automated recovery procedures
   - Dependency-aware health evaluation
   - Self-healing mechanisms

2. **Deployment and Update Management**
   - Zero-downtime deployment strategies
   - Traffic shifting and load balancing
   - Deployment verification
   - Automated rollback mechanisms

3. **Resilience Testing Infrastructure**
   - Fault injection capabilities
   - Chaos experiment coordination
   - Resilience verification
   - Experiment reporting and documentation

4. **Resource Management and Scaling**
   - Dynamic scaling based on demand
   - Resource utilization monitoring
   - Cost optimization strategies
   - Capacity planning tools

5. **Observability Infrastructure**
   - Distributed tracing implementation
   - Structured logging system
   - Metrics collection and aggregation
   - Performance analysis tools

## Testing Requirements

### Key Functionalities that Must be Verified
- Automatic recovery from various failure scenarios
- Zero-downtime deployment with traffic shifting
- Resilience under chaos testing conditions
- Dynamic scaling based on load conditions
- End-to-end transaction tracing

### Critical User Scenarios
- Recovery from service instance failures
- Deployment of service updates without disruption
- System behavior under resource constraints
- System response to sudden traffic spikes
- Troubleshooting complex transaction failures

### Performance Benchmarks
- Recover failed services within 30 seconds
- Complete zero-downtime deployments within 5 minutes
- Scale up to handle 3x traffic increase within 2 minutes
- Trace and log 10,000+ transactions per second
- Support 1,000+ service instances with comprehensive monitoring

### Edge Cases and Error Conditions
- Cascading failures across service dependencies
- Partial network partitions
- Resource exhaustion scenarios
- Corrupt configuration deployments
- Data inconsistency during recovery

### Required Test Coverage Metrics
- Minimum 90% line coverage for all code
- 100% coverage of recovery mechanisms
- 100% coverage of deployment orchestration
- 100% coverage of chaos testing functionality
- 100% coverage of scaling logic

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

The implementation will be considered successful if:

1. Services automatically recover from common failure scenarios
2. Deployments can be performed without service disruption
3. The system demonstrates resilience under chaos testing
4. Resources scale dynamically based on demand
5. Distributed transactions can be traced across service boundaries
6. Performance meets the specified benchmarks
7. All test cases pass with the required coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up the development environment:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install test dependencies
uv pip install pytest pytest-json-report

# Run tests and generate the required JSON report
pytest --json-report --json-report-file=pytest_results.json
```

CRITICAL: Generating and providing the pytest_results.json file is a mandatory requirement for project completion. This file serves as evidence that all functionality has been implemented correctly and passes all tests.