# IoT Protocol Efficiency Analyzer

## Overview
A specialized network protocol analysis library designed for IoT device developers to optimize network communications by analyzing protocol efficiency, power consumption patterns, packet fragmentation, timing characteristics, and custom lightweight protocol validation for resource-constrained devices.

## Persona Description
Raj develops firmware for Internet of Things devices with severe bandwidth and power constraints. He needs to optimize network communications by analyzing protocol efficiency and identifying unnecessary overhead in device communications.

## Key Requirements

1. **Protocol Efficiency Scoring System**  
   Create a module that analyzes and scores different protocol implementation options against bandwidth usage metrics. This is critical for Raj because IoT devices operate with strict bandwidth limitations, and choosing the most efficient protocol implementation can significantly extend battery life and improve device responsiveness.

2. **Power Consumption Estimation**  
   Implement functionality to correlate network activity patterns with estimated energy requirements. This feature is essential for Raj to optimize firmware for battery-powered IoT devices, helping identify communication patterns that cause unnecessary power drain and providing data to make informed tradeoffs between functionality and battery life.

3. **Packet Fragmentation Analysis**  
   Develop capabilities to identify issues with MTU sizing and packet reassembly. This is crucial for Raj because fragmented packets increase overhead, waste bandwidth, and require more processing power to reassemble. Optimizing packet sizes to avoid fragmentation can significantly improve both performance and power efficiency.

4. **Timing Visualization and Analysis**  
   Build a system to analyze communication delays, protocol synchronization issues, and timing patterns. This allows Raj to identify inefficient polling intervals, unnecessary acknowledgment sequences, and optimize wake/sleep cycles, which directly impacts both device responsiveness and battery life.

5. **Custom Lightweight Protocol Validation**  
   Create functionality to validate compliance with custom lightweight protocol specifications. This feature is vital for Raj as it allows him to verify that his custom protocol implementations correctly adhere to specifications, ensuring interoperability while maintaining the minimal possible overhead for resource-constrained devices.

## Technical Requirements

### Testability Requirements
- All components must be testable with synthetic and real-world IoT traffic datasets
- Protocol efficiency scoring must be testable with comparison baselines
- Power estimation algorithms must be verifiable with known power consumption profiles
- Timing analysis must be validated against precise clock references
- Custom protocol validation must be testable against formal protocol specifications

### Performance Expectations
- Process at least 24 hours of IoT device traffic data in under 5 minutes
- Calculate protocol efficiency scores for 10 different protocol variants in under 30 seconds
- Analyze timing characteristics with microsecond precision
- Process fragmentation analysis for 10,000 packet transmissions in under 10 seconds
- Support analyzing extremely small payloads (1-100 bytes) efficiently

### Integration Points
- Import traffic from standard PCAP/PCAPNG files
- Export analysis reports in CSV and JSON formats
- Support for importing custom protocol specifications in standardized formats
- Interface with power profiling hardware data when available
- Compatibility with common IoT protocol analyzers for cross-validation

### Key Constraints
- Must run efficiently on development workstations with 8GB RAM
- Analysis must work with limited packet capture samples (incomplete traffic)
- Must handle non-standard and custom IoT protocols
- Analysis should be usable in offline environments without external dependencies
- Must process extremely low bandwidth communications (bits per second) accurately

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The IoT Protocol Efficiency Analyzer should provide the following core functionality:

1. **Protocol Analysis Engine**
   - Parse and decode standard IoT protocols (MQTT, CoAP, LwM2M, etc.)
   - Support for custom protocol parsing with user-defined specifications
   - Comparative analysis between protocol variants
   - Byte-level overhead measurement and optimization suggestions

2. **Energy Efficiency Analysis**
   - Model power consumption based on protocol characteristics
   - Identify radio transmission patterns and optimization opportunities
   - Analyze sleep/wake cycles and their efficiency
   - Correlate protocol choices with theoretical battery impact

3. **Packet Optimization Tools**
   - Analyze MTU utilization and fragmentation rates
   - Suggest optimal packet sizes for different network conditions
   - Identify compression opportunities in repeated data patterns
   - Simulate performance impact of packet size modifications

4. **Timing Analysis System**
   - Measure and analyze protocol timing patterns
   - Identify synchronization issues and their causes
   - Detect unnecessary polling or keepalive messages
   - Suggest optimal timing parameters for various operations

5. **Protocol Validation Framework**
   - Define and validate custom protocol specifications
   - Verify protocol compliance and implementation correctness
   - Detect protocol deviations and specification violations
   - Provide detailed protocol conformance reports

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of protocol parsing and decoding
- Correctness of efficiency scoring calculations
- Precision of power consumption estimates
- Accuracy of fragmentation analysis
- Effectiveness of custom protocol validation

### Critical User Scenarios
- Comparing efficiency of MQTT vs. CoAP for a specific use case
- Analyzing power consumption patterns of a battery-powered sensor
- Identifying optimal packet sizes for unreliable network conditions
- Optimizing polling intervals for a time-sensitive application
- Validating a custom lightweight protocol implementation

### Performance Benchmarks
- Process at least 1,000 packets per second on reference hardware
- Complete efficiency scoring of 5 protocol variants in under 15 seconds
- Achieve power estimation accuracy within 10% of measured values
- Analyze timing characteristics with at least microsecond resolution
- Validate protocol compliance with 100% detection of specification violations

### Edge Cases and Error Conditions
- Handling extremely small packet sizes (1-10 bytes)
- Processing intermittent, non-continuous traffic captures
- Analyzing protocols with variable-length fields
- Supporting devices with extremely limited bandwidth (bits per second)
- Handling encrypted or partially encrypted IoT communications

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for protocol efficiency scoring
- 95% coverage for power consumption estimation
- 90% coverage for packet fragmentation analysis
- 95% coverage for custom protocol validation

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

The IoT Protocol Efficiency Analyzer implementation will be considered successful when:

1. It can accurately score protocol efficiency for at least 5 common IoT protocols with clear comparative metrics
2. It provides power consumption estimates within 10% accuracy compared to reference measurements
3. It correctly identifies packet fragmentation issues and provides actionable size recommendations
4. It analyzes timing patterns with sufficient precision to optimize polling and wake/sleep cycles
5. It validates custom protocol implementations with 100% detection of specification violations

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Project Setup and Environment

To set up the project environment:

1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Install development dependencies including pytest-json-report

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

The pytest_results.json file serves as verification that all functionality works as required and all tests pass successfully. This file must be generated and included with your submission.