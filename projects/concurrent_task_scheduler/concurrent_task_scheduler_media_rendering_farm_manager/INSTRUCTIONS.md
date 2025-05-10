# Render Farm Task Orchestrator

A concurrent task scheduler designed specifically for managing 3D rendering workloads across distributed rendering nodes with deadline awareness and resource optimization.

## Overview

The Render Farm Task Orchestrator is a specialized task scheduling framework for managing complex animation and visual effects rendering operations. It implements deadline-driven scheduling with dynamic priority adjustment, resource partitioning for multiple clients, rendering node specialization, progressive result generation, and cost/power optimization for efficient resource usage.

## Persona Description

Carlos oversees a 3D rendering operation that processes animation and visual effects for film studios. His primary goal is to balance rendering jobs across hundreds of machines while adapting to changing project priorities and deadlines.

## Key Requirements

1. **Deadline-Driven Scheduling System**
   - Scheduling framework that automatically adjusts task priorities based on approaching deadlines and remaining work
   - Critical for Carlos because film production schedules have strict delivery deadlines, and the system must dynamically reprioritize rendering tasks to ensure all projects meet their delivery dates even as priorities and deadlines shift

2. **Client Resource Partitioning**
   - Resource allocation system that divides rendering capacity between different clients/projects with guaranteed minimum resources per client
   - Essential because the rendering farm serves multiple production studios simultaneously, and each client needs guaranteed capacity while allowing for efficient utilization of any unused capacity across projects

3. **Render Node Specialization**
   - Task allocation system that matches rendering jobs to specialized hardware based on rendering characteristics
   - Important because different rendering tasks (character animation, fluid simulation, lighting) have unique computational profiles that perform optimally on different hardware configurations, requiring intelligent matching for maximum efficiency

4. **Progressive Result Generation**
   - Framework for generating preliminary rendering results before full-quality completion
   - Valuable for providing early feedback to artists and directors, allowing them to identify issues and make creative decisions without waiting for final high-quality renders to complete

5. **Power/Cost Optimization**
   - Scheduling modes that optimize for reduced power consumption or cost during different operational periods
   - Critical for balancing operational expenses by scheduling intensive rendering during off-peak electricity hours and implementing power-saving strategies when appropriate without missing deadlines

## Technical Requirements

### Testability Requirements
- Rendering job simulation framework for testing without actual renderers
- Deadline scenarios must be reproducibly testable
- Resource allocation decisions must be verifiable
- Performance characteristics must be measurable in test environments

### Performance Expectations
- Support for managing at least 10,000 concurrent rendering tasks
- Scheduling decisions completed in under 100ms for the entire render farm
- Resource utilization maintained above 85% during normal operation
- Priority recalculation within 5 seconds of deadline changes

### Integration Points
- Rendering software command-line interfaces (e.g., Arnold, V-Ray)
- Job submission API for client integration
- Result storage and delivery system
- Monitoring and reporting interfaces

### Key Constraints
- Minimal dependencies on specific rendering software
- Support for heterogeneous rendering node configurations
- No rendering node downtime during rescheduling
- Fault tolerance for node failures

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Render Farm Task Orchestrator should provide the following core functionality:

1. **Rendering Task and Job Management**
   - Python API for defining rendering jobs and their components
   - Deadline and priority specification
   - Resource requirement declarations

2. **Intelligent Scheduling**
   - Deadline-based priority calculation
   - Client resource allocation and isolation
   - Node-appropriate task assignment
   - Dynamic rebalancing as conditions change

3. **Resource Optimization**
   - Hardware-task matching algorithms
   - Power usage management
   - Cost-aware scheduling
   - Idle resource reallocation

4. **Execution and Monitoring**
   - Distributed task execution
   - Progress tracking and estimation
   - Early result generation
   - Failure detection and recovery

5. **Reporting and Analysis**
   - Resource utilization analytics
   - Client usage accounting
   - Performance optimization recommendations
   - Deadline compliance reporting

## Testing Requirements

### Key Functionalities to Verify
- Tasks are correctly prioritized based on deadlines
- Resource guarantees for clients are maintained
- Rendering jobs are matched to appropriate hardware
- Progressive results are generated according to schedule
- Power/cost optimization reduces operational expenses

### Critical User Scenarios
- Multiple projects with competing deadlines
- Sudden deadline changes requiring reprioritization
- Hardware failure requiring task redistribution
- Mixed workload of short and long-running renders
- Off-hours optimization without missing deadlines

### Performance Benchmarks
- Scheduling overhead less than 1% of rendering time
- Client resource guarantees met 100% of the time
- Specialized hardware matching improves throughput by 25%
- Progressive results available within 10% of job start time
- Power optimization reduces consumption by at least 15% during off-hours

### Edge Cases and Error Conditions
- Deadline conflicts between projects
- Resource exhaustion under peak demand
- Hardware failure during critical renders
- Corrupt or incomplete render results
- Priority inversion during rescheduling

### Required Test Coverage Metrics
- 95% line coverage for core scheduling algorithms
- All deadline calculation paths tested
- Complete coverage of resource allocation logic
- Full testing of node specialization matching
- Power optimization strategies verified for all scenarios

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. All rendering projects meet their deadlines with appropriate prioritization
2. Each client receives their guaranteed minimum resource allocation
3. Rendering tasks consistently execute on the most appropriate hardware
4. Progressive results are available for feedback early in the rendering process
5. Power and cost optimizations reduce operational expenses by at least 15%
6. The system scales effectively to manage 10,000+ concurrent tasks
7. All tests pass, including edge cases and error conditions
8. Resource utilization remains above 85% during normal operation

## Setup and Development

To set up the development environment:

```bash
# Initialize the project with uv
uv init --lib

# Install development dependencies
uv sync
```

To run the code:

```bash
# Run a script
uv run python script.py

# Run tests
uv run pytest
```