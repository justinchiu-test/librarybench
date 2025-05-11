# Industrial Control Systems Protocol Analyzer

## Overview
A specialized network protocol analysis library focused on industrial control systems (ICS) and SCADA environments, providing industrial protocol decoding, safety boundary monitoring, timing anomaly detection, air-gap verification, and baseline deviation alerting for critical operational technology networks.

## Persona Description
Hannah monitors network traffic for industrial control systems (ICS) and SCADA environments. She needs to ensure these critical systems remain secure while identifying potential safety issues in their communication patterns.

## Key Requirements

1. **Industrial Protocol Decoders**  
   Create a module that parses and analyzes specialized industrial formats like Modbus, DNP3, BACnet, Profinet, and other ICS protocols. This is critical for Hannah because industrial protocols differ significantly from IT protocols, and understanding their specific commands and parameters is essential for monitoring the security and operational integrity of critical infrastructure systems.

2. **Safety Boundary Monitoring**  
   Implement functionality to verify that critical commands stay within operational limits and predefined safety parameters. This feature is essential for Hannah to detect potentially dangerous control commands that could cause physical damage, safety hazards, or operational disruptions in industrial environments, providing an early warning system for both security and safety incidents.

3. **Timing Anomaly Detection**  
   Develop capabilities to identify deviations from normal timing patterns in industrial communications that could disrupt real-time operations. This is crucial for Hannah because many industrial processes are time-sensitive, and delays or irregular communication patterns can indicate cyber attacks, equipment failures, or conditions that could lead to operational disruptions.

4. **Air-gap Verification**  
   Build a system to confirm proper isolation between IT networks and operational technology (OT) networks. This allows Hannah to verify that critical industrial systems maintain proper network segregation, ensuring that potential compromise of corporate IT networks doesn't create vectors for attacks against sensitive control systems that could impact safety or production.

5. **Baseline Deviation Alerting**  
   Create functionality to detect when industrial systems communicate in unusual patterns compared to their established baselines. This feature is vital for Hannah to identify subtle signs of compromise, misconfiguration, or emerging technical problems in industrial systems that often maintain very consistent and predictable communication patterns during normal operations.

## Technical Requirements

### Testability Requirements
- All components must be testable with ICS protocol datasets
- Industrial protocol decoders must be verifiable against protocol specifications
- Safety boundary monitoring must be testable with predefined safe/unsafe values
- Timing analysis must be validated with precise timing reference datasets
- Baseline deviation detection must be verifiable against known normal/abnormal patterns

### Performance Expectations
- Process at least 24 hours of ICS traffic data in under 10 minutes
- Support real-time analysis of multiple control system networks simultaneously
- Decode industrial protocols with minimal latency (< 100ms per message)
- Detect timing anomalies with microsecond precision
- Generate alerts within 2 seconds of detecting significant deviations

### Integration Points
- Import traffic from standard PCAP/PCAPNG files and industrial protocol analyzers
- Support for reading industrial protocol specifications and device profiles
- Export findings in formats compatible with industrial security systems
- Integration with process historians for correlation with operational data
- Support for importing safety thresholds from industrial risk assessments

### Key Constraints
- Must function in air-gapped environments without external dependencies
- Analysis should not impact operational network performance
- Must handle proprietary and vendor-specific protocol variations
- Should operate with minimal CPU/memory footprint on industrial systems
- Must support both modern and legacy (20+ years old) industrial protocols

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Industrial Control Systems Protocol Analyzer should provide the following core functionality:

1. **Industrial Protocol Analysis Engine**
   - Parse and decode common industrial protocols (Modbus, DNP3, BACnet, etc.)
   - Interpret protocol-specific commands and parameters
   - Support for proprietary protocol extensions
   - Detailed analysis of control operations and their implications

2. **Safety and Security Analysis**
   - Verification of command parameters against operational limits
   - Detection of potentially hazardous command sequences
   - Identification of unauthorized control attempts
   - Analysis of command timing and sequencing safety

3. **Real-time Communication Analysis**
   - Precise timing measurement of industrial communications
   - Detection of jitter, delays, and communication interruptions
   - Analysis of polling patterns and response times
   - Identification of timing-based attack patterns

4. **Network Segmentation Verification**
   - Detection of traffic crossing IT/OT boundaries
   - Verification of proper network isolation
   - Identification of potential air-gap violations
   - Analysis of data flows between network segments

5. **Behavioral Baseline Monitoring**
   - Establishment of normal communication patterns
   - Statistical analysis of protocol usage over time
   - Detection of anomalous communication patterns
   - Correlation of communications with operational states

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of industrial protocol parsing and interpretation
- Correctness of safety boundary detection
- Precision of timing anomaly identification
- Effectiveness of air-gap verification
- Reliability of baseline deviation detection

### Critical User Scenarios
- Analyzing Modbus traffic controlling critical infrastructure
- Detecting out-of-range control values that could cause safety issues
- Identifying unusual timing patterns in PLC communications
- Verifying that no unauthorized traffic crosses IT/OT boundaries
- Alerting on unusual communication patterns from a factory controller

### Performance Benchmarks
- Decode at least 1,000 industrial protocol messages per second
- Complete safety boundary analysis in real-time with no processing backlog
- Detect timing anomalies with less than 100 microsecond resolution
- Process network segmentation verification for 100 devices in under 30 seconds
- Establish baseline patterns from 7 days of traffic data in under 30 minutes

### Edge Cases and Error Conditions
- Handling proprietary or undocumented protocol extensions
- Processing degraded or partial communications during system issues
- Analyzing extremely time-sensitive protocols (microsecond precision)
- Dealing with protocol violations and malformed messages
- Supporting legacy systems with unusual communication patterns

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for industrial protocol decoders
- 95% coverage for safety boundary monitoring
- 90% coverage for timing anomaly detection
- 95% coverage for baseline deviation alerting

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

The Industrial Control Systems Protocol Analyzer implementation will be considered successful when:

1. It correctly decodes and interprets at least 5 major industrial protocols with proper command analysis
2. It successfully identifies control commands that exceed safe operational boundaries
3. It detects timing anomalies that could impact real-time industrial operations
4. It verifies network segmentation and alerts on potential air-gap violations
5. It establishes communication baselines and identifies deviations that could indicate security or operational issues

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