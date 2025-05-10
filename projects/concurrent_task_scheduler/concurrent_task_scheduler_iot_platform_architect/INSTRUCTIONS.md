# IoT Data Processing Scheduler

A concurrent task scheduler optimized for handling IoT data streams with elastic scaling, tiered processing, and anomaly detection.

## Overview

The IoT Data Processing Scheduler is a specialized task execution framework designed for processing data from millions of connected devices. It implements elastic scaling based on incoming data patterns, prioritized processing for premium device tiers, regional processing optimization, anomaly detection workflows, and resource reservation for maintenance operations.

## Persona Description

Amara designs backend systems for an IoT platform processing data from millions of connected devices. Her primary goal is to handle unpredictable bursts of incoming data while ensuring time-sensitive analytics are completed reliably.

## Key Requirements

1. **Elastic Scaling System**
   - Dynamic resource allocation framework that automatically scales processing capacity based on detected patterns in incoming data volume
   - Critical for Amara because IoT data arrives in unpredictable patterns with significant volume spikes during certain times of day or triggered by external events, requiring adaptive capacity to maintain processing SLAs

2. **Tiered Data Processing**
   - Prioritization mechanism that ensures data from premium device tiers receives processing preference during high load periods
   - Essential for implementing service level differentiation where certain customers or critical device categories receive guaranteed processing capacity regardless of system load

3. **Regional Processing Optimization**
   - Scheduling strategy that minimizes data transfer by processing data close to its geographic origin when possible
   - Important for reducing data transfer costs and latency in a globally distributed IoT platform, optimizing both operational efficiency and response times across different geographic regions

4. **Anomaly Detection Prioritization**
   - Workflow system that allows critical anomaly detection processes to preempt routine data processing when necessary
   - Vital for quickly identifying and responding to abnormal device behavior or security threats which require immediate attention even if it means temporarily delaying routine data processing

5. **Maintenance Resource Reservation**
   - Capacity management system that reserves resources for scheduled platform maintenance operations
   - Necessary for ensuring that system maintenance can proceed without disrupting critical data processing, preventing maintenance operations from competing with normal workloads for resources

## Technical Requirements

### Testability Requirements
- Simulated data ingestion for load testing
- Reproducible pattern generation for scaling tests
- Geographical distribution simulation
- Anomaly injection for detection testing

### Performance Expectations
- Support for processing data from at least 1 million concurrent devices
- Scaling response within 30 seconds of load pattern changes
- Processing latency under 500ms for premium tier data
- Anomaly detection within 5 seconds of occurrence

### Integration Points
- Data ingestion pipeline interface
- Device registry for tier information
- Geographic distribution mapping
- Alerting systems for anomaly notification

### Key Constraints
- Must operate within cloud resource limits
- Data locality and privacy requirements
- Bounded response time guarantees
- Cost optimization considerations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The IoT Data Processing Scheduler should provide the following core functionality:

1. **Data Ingestion and Classification**
   - High-throughput data reception from IoT devices
   - Message classification by device tier and type
   - Geographical tagging and routing

2. **Resource Management**
   - Dynamic worker pool scaling
   - Regional resource allocation
   - Capacity reservation and management
   - Load prediction and preemptive scaling

3. **Task Scheduling and Execution**
   - Priority-based task assignment
   - Geographically-optimized processing
   - Preemptive task scheduling for critical workloads
   - Task timeout and retry mechanisms

4. **Anomaly Processing**
   - Pattern deviation detection
   - Priority escalation for anomalies
   - Accelerated processing pipelines for critical events
   - Correlation across multiple devices

5. **Operational Management**
   - Maintenance window scheduling
   - Resource utilization monitoring
   - Performance metrics collection
   - Scaling efficiency analysis

## Testing Requirements

### Key Functionalities to Verify
- Processing capacity scales correctly with changing data volumes
- Premium tier devices receive priority processing
- Data is processed in the optimal geographic region
- Anomaly detection workflows preempt routine processing
- Maintenance operations receive their reserved resources

### Critical User Scenarios
- Sudden spike in data volume with elastic scaling response
- Mixed workload of different device tiers during peak load
- Geographically diverse data sources with regional processing
- Anomaly detection during high system load
- Scheduled maintenance during normal operations

### Performance Benchmarks
- Scaling responsiveness within 30 seconds of load change
- Processing throughput of at least 100,000 messages per second
- Premium tier processing latency under 500ms at all times
- Anomaly detection within 5 seconds of event occurrence
- Less than 5% resource wastage during normal operations

### Edge Cases and Error Conditions
- Extreme data volume spikes beyond scaling capacity
- Network partitioning between regions
- Resource exhaustion during peak load
- Cascading anomalies across multiple device groups
- Failed maintenance operations requiring rescheduling

### Required Test Coverage Metrics
- 95% code coverage for scaling logic
- Full test coverage of priority processing workflows
- Complete testing of geographic optimization algorithms
- All anomaly detection paths verified
- Comprehensive testing of maintenance reservation scenarios

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. The system automatically scales to handle varying data volumes within 30 seconds
2. Premium tier devices consistently experience processing latencies under 500ms
3. Data processing is optimally distributed to minimize transfer costs
4. Anomalies are detected and processed within 5 seconds
5. Maintenance operations proceed without resource contention
6. The system maintains throughput during unexpected data volume changes
7. All tests pass, including edge cases and error conditions
8. The system effectively manages resources to minimize operational costs

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