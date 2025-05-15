# IoT Data Processing Orchestrator

## Overview
A specialized concurrent task scheduler designed for IoT platforms processing data from millions of connected devices. This system handles unpredictable bursts of incoming data while ensuring time-sensitive analytics are completed reliably, with particular focus on elastic scaling, tiered processing, regional optimization, and anomaly response.

## Persona Description
Amara designs backend systems for an IoT platform processing data from millions of connected devices. Her primary goal is to handle unpredictable bursts of incoming data while ensuring time-sensitive analytics are completed reliably.

## Key Requirements

1. **Elastic Scaling Framework**
   - Implement an intelligent scaling system that automatically adjusts processing capacity based on incoming data volume patterns
   - This feature is critical for Amara as IoT data ingestion is highly variable, with sudden bursts during device synchronization events and daily/weekly usage patterns
   - The system must scale processing tasks up and down efficiently while maintaining cost-effectiveness and ensuring all data is processed within latency constraints

2. **Tiered Data Processing System**
   - Create a multi-level prioritization mechanism that provides premium service levels for high-priority devices or customers
   - This feature is essential for Amara to implement business-driven SLAs where certain customers or device categories (e.g., medical, industrial safety) require guaranteed processing performance
   - Must support configurable tier definitions with resource guarantees and maximum latency bounds

3. **Regional Processing Optimization**
   - Develop a location-aware task distribution system that minimizes data transfer by processing information close to its source when possible
   - This feature is crucial for Amara as IoT deployments are globally distributed, and unnecessary data transfer increases both costs and latency
   - Must balance regional processing efficiency against global resource utilization and regulatory requirements

4. **Anomaly Detection Workflow**
   - Implement specialized processing paths for anomalous data that can preempt routine processing when urgent conditions are detected
   - This feature is vital for Amara to ensure that critical events (security breaches, equipment failures, safety conditions) receive immediate attention even during high system load
   - Must include configurable anomaly definitions and escalation policies based on severity

5. **Maintenance Window Management**
   - Create a resource reservation system for scheduled maintenance operations that ensures sufficient capacity without disrupting critical data processing
   - This feature is important for Amara to perform system upgrades, index rebuilding, and other maintenance tasks without impacting the platform's ability to handle incoming device data
   - Must support advance scheduling with dynamic adjustment based on actual system load

## Technical Requirements

### Testability Requirements
- All components must be independently testable with well-defined interfaces
- System must support simulation of large-scale IoT data patterns without real devices
- Test coverage should exceed 90% for all data ingestion and processing components
- Tests must validate behavior under various data volume scenarios and anomaly conditions

### Performance Expectations
- Support for processing data from at least 1 million concurrent IoT devices
- Ability to handle burst ingestion rates of up to 100,000 messages per second
- Scaling operations must complete within 30 seconds of detecting load changes
- End-to-end processing latency for high-priority data should not exceed 500ms

### Integration Points
- Integration with common IoT protocols (MQTT, CoAP, AMQP)
- Support for cloud provider auto-scaling services (AWS, Azure, GCP)
- Interfaces for monitoring and alerting systems
- Compatibility with data lake and analytics platforms

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- The system must maintain data processing guarantees even during scaling operations
- All operations must be auditable for compliance and troubleshooting
- Must operate efficiently in multi-region cloud environments
- System must be resilient to network partitions and region failures

## Core Functionality

The IoT Data Processing Orchestrator must provide:

1. **Data Ingestion and Classification**
   - High-throughput mechanisms for receiving data from diverse IoT sources
   - Classification of incoming data based on source, type, and content
   - Initial triage for time-sensitive or anomalous information

2. **Adaptive Resource Management**
   - Dynamic scaling of processing resources based on current and predicted load
   - Balancing of workloads across available processing units
   - Reservation of capacity for high-priority devices and operations

3. **Processing Pipeline Orchestration**
   - Definition and execution of multi-stage data processing workflows
   - Routing of data through appropriate regional processing centers
   - Special handling for anomalous or priority data

4. **Monitoring and Optimization**
   - Collection of detailed performance metrics across processing stages
   - Predictive modeling of resource requirements based on historical patterns
   - Continuous optimization of task placement and scheduling

5. **Maintenance and Administration**
   - Controlled scheduling of system maintenance operations
   - Graceful handover during software updates and reconfigurations
   - Management of regional processing capacity

## Testing Requirements

### Key Functionalities to Verify
- Elastic scaling correctly adjusts processing capacity based on load
- Tiered processing properly prioritizes data based on source and content
- Regional optimization effectively minimizes unnecessary data transfer
- Anomaly workflows correctly identify and prioritize critical events
- Maintenance reservations ensure sufficient capacity without disruption

### Critical Scenarios to Test
- Response to sudden spikes in data volume from specific regions
- Handling of mixed priority traffic during peak load periods
- Management of critical anomalies during system maintenance
- Recovery from simulated regional outages or network partitions
- Performance under sustained high-volume data ingestion

### Performance Benchmarks
- Elastic scaling should initiate within 10 seconds of detecting significant load changes
- High-priority data should be processed with at least 3x lower latency than standard data
- Regional processing should reduce cross-region data transfer by at least 80%
- Anomaly detection should identify critical events within 100ms of ingestion
- Maintenance operations should proceed without increasing processing latency for critical data

### Edge Cases and Error Conditions
- Handling of malformed data or protocol violations
- Recovery from worker node failures during processing
- Correct behavior during partial network outages
- Proper prioritization when anomalies exceed processing capacity
- Graceful degradation when total ingestion exceeds maximum scaling capacity

### Required Test Coverage
- Minimum 90% line coverage for all data ingestion and processing components
- Comprehensive integration tests for end-to-end data workflows
- Performance tests simulating production-scale IoT data patterns
- Stress tests for maximum load conditions and failure scenarios

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

1. Elastic scaling adjusts capacity to maintain processing SLAs across varying loads
2. Tiered processing guarantees lower latency for high-priority data sources
3. Regional optimization reduces cross-region data transfer by at least 80%
4. Anomaly detection workflows process critical events within 100ms
5. Maintenance reservations allow system operations without impacting critical processing

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using UV:
   ```
   uv venv
   source .venv/bin/activate
   ```

2. Install the project in development mode:
   ```
   uv pip install -e .
   ```

3. CRITICAL: Run tests with pytest-json-report to generate pytest_results.json:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.