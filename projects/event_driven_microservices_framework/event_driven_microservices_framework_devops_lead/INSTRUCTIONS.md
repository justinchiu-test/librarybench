# DevOps-Focused Event-Driven Microservices Framework

## Overview
A resilient microservices framework optimized for operational excellence that enables automated deployment, monitoring, and self-healing capabilities. This framework focuses on providing a robust infrastructure for deploying and managing distributed services with minimal operational overhead while maintaining system reliability.

## Persona Description
Alex manages infrastructure for a rapidly growing startup that needs to scale services quickly without compromising reliability. His primary goal is to implement a microservices platform with robust operational characteristics that supports automated deployment, monitoring, and recovery to minimize operational overhead.

## Key Requirements

1. **Service Health Monitoring with Automated Recovery Mechanisms**
   - Implement comprehensive health check protocols for services that detect various failure types (unresponsive, degraded, etc.)
   - Create automated recovery strategies that can restart, redeploy, or reroute traffic away from unhealthy services
   - This feature is critical for Alex as it minimizes manual intervention during incidents and ensures high availability through automated self-healing

2. **Deployment Orchestration with Zero-Downtime Updates**
   - Develop a deployment coordination system that enables rolling updates, blue-green deployments, and canary releases
   - Implement automatic rollback mechanisms when deployments trigger health check failures
   - This capability is essential for Alex's team to deploy updates continuously without affecting users, minimizing deployment risk while maximizing delivery speed

3. **Chaos Testing Integration for Resilience Verification**
   - Create a controlled chaos testing framework that can inject failures at the network, service, and system levels
   - Include scheduling capabilities for conducting regular resilience tests in various environments
   - This feature allows Alex to proactively identify system weaknesses and verify that recovery mechanisms work correctly before production incidents occur

4. **Resource Utilization Optimization with Dynamic Scaling**
   - Develop metrics collection and analysis to identify resource usage patterns across services
   - Create automatic scaling policies that adjust service instances based on traffic patterns and resource consumption
   - This capability ensures Alex's infrastructure efficiently utilizes resources, controlling costs while maintaining performance during traffic spikes

5. **Comprehensive Tracing and Logging Infrastructure**
   - Implement distributed tracing that follows events across multiple service boundaries
   - Create structured logging with correlation IDs and standardized formats
   - This feature enables Alex to quickly identify the root cause of issues in a distributed system, significantly reducing time to resolution and providing insights for system improvements

## Technical Requirements

### Testability Requirements
- All components must be testable in isolation with dependency injection
- Chaos testing scenarios must be reproducible with controlled fault injection
- Mock implementations of health check and monitoring systems for testing failure scenarios
- Synthetic load generation capabilities for testing scaling functionality
- Tracing and logging subsystems must support test verification

### Performance Expectations
- Service health checks must complete within 1 second
- Recovery actions must initiate within 3 seconds of detecting failures
- Deployment operations must avoid any service interruption (zero downtime)
- Scaling operations must complete within 30 seconds of detection of load changes
- Tracing overhead must not exceed 5% of service CPU utilization

### Integration Points
- Integration with container orchestration platforms (design for compatibility)
- Standardized health check endpoints across all services
- Metrics collection endpoints for external monitoring systems
- Event publishing interfaces for deployment events
- Pluggable logging destinations for integration with existing log aggregation solutions

### Key Constraints
- All functionality must work within a mixed deployment environment (containers, VMs, etc.)
- Framework must operate with minimal resource overhead on service instances
- Must function correctly in network-constrained environments (intermittent connectivity)
- Should not require specialized hardware or cloud-specific services
- All operational data must be accessible through APIs for external tooling

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide the following core functionality:

1. **Service Registry and Discovery**
   - Service registration with metadata and health endpoint information
   - Service discovery mechanism for locating healthy service instances
   - Dynamic endpoint resolution with client-side load balancing

2. **Health Monitoring System**
   - Configurable health check executors with multiple check types
   - Health status aggregation and history tracking
   - Failure detection with configurable thresholds and sensitivity

3. **Recovery Orchestration**
   - Recovery action framework with pluggable strategies
   - Recovery policy enforcement based on service type and failure patterns
   - Coordinated recovery to prevent cascading failures or recovery storms

4. **Event-based Communication**
   - Reliable event bus with delivery guarantees
   - Event schema versioning and compatibility checking
   - Priority-based event processing for operational events

5. **Deployment Coordination**
   - Deployment state tracking and version management
   - Traffic shifting controls for gradual deployment
   - Deployment verification through automated health verification

6. **Resource Metrics and Scaling**
   - Resource utilization tracking at service and instance levels
   - Predictive scaling based on historical patterns
   - Scheduled scaling for anticipated traffic increases

7. **Distributed Tracing**
   - Trace context propagation across service boundaries
   - Sampling policies for controlling tracing overhead
   - Trace aggregation and analysis utilities

8. **Chaos Testing Framework**
   - Configurable fault injectors for various failure types
   - Test scenario definition and execution
   - Resilience verification reporting

## Testing Requirements

### Key Functionalities That Must Be Verified
- Automated recovery correctly restores service health after various failure types
- Zero-downtime deployments maintain service availability during updates
- Chaos tests accurately simulate real-world failure scenarios
- Dynamic scaling correctly responds to changing load patterns
- Distributed tracing captures complete request flows across services

### Critical User Scenarios
- Service instance failure triggers automatic recovery
- Service deployment with traffic shifting occurs without errors
- System maintains availability during simulated infrastructure failures
- Services scale up and down in response to load changes
- Operators can trace requests through the system to identify bottlenecks

### Performance Benchmarks
- Recovery mechanisms restore service within defined SLO timeframes
- Deployment operations complete within expected timeframes
- System handles peak loads with automatic scaling
- Tracing and logging functions have minimal impact on system performance

### Edge Cases and Error Conditions
- Multiple simultaneous service failures
- Network partitioning between services
- Corrupted or incompatible deployment artifacts
- Cascading failures across service dependencies
- Resource exhaustion scenarios

### Required Test Coverage Metrics
- Minimum 90% line coverage for all components
- 100% coverage of recovery and deployment logic
- All chaos testing scenarios must be tested in isolation
- All error handling and recovery paths must be explicitly tested
- All service scaling triggers must be verified

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- All services maintain 99.9% availability even during deployment and infrastructure disruptions
- Recovery from service failures occurs within 30 seconds without manual intervention
- Deployment failures are automatically detected and rolled back within 60 seconds
- Resource utilization remains within 10% of optimal levels through automatic scaling
- Operators can identify the root cause of issues within 5 minutes using the tracing and logging system
- All chaos testing scenarios are routinely passed, verifying system resilience
- Zero operational incidents caused by deployment activities
- System correctly handles traffic spikes by scaling to meet demand without manual intervention

## Getting Started

To set up the development environment for this project:

1. Initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install dependencies using `uv sync`

3. Run tests using `uv run pytest`

4. To execute specific Python scripts:
   ```
   uv run python your_script.py
   ```

5. For running linters and type checking:
   ```
   uv run ruff check .
   uv run pyright
   ```

Remember to design the framework as a library with well-documented APIs, not as an application with user interfaces. All functionality should be exposed through programmatic interfaces that can be easily tested and integrated into larger systems.