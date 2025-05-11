# Enterprise Network Analysis Framework

## Overview
A comprehensive network protocol analysis library designed for enterprise network administrators to troubleshoot performance bottlenecks, verify network segmentation, map service dependencies, analyze bandwidth utilization, and validate network configurations and quality of service implementations.

## Persona Description
Michael manages network infrastructure for a large corporation with complex connectivity requirements. He needs to troubleshoot performance bottlenecks, identify misconfigured services, and ensure proper segmentation between network zones.

## Key Requirements

1. **VLAN Boundary Analysis**  
   Create a module that verifies traffic segregation between network segments by analyzing packet flows across VLANs and security zones. This is critical for Michael because improper network segmentation can lead to serious security vulnerabilities, compliance violations, and inefficient traffic routing in a complex enterprise environment.

2. **Service Dependency Mapping**  
   Implement functionality to discover and visualize which systems communicate with each other, identifying critical dependencies and communication patterns. This feature is essential for Michael to understand the impact of network changes, plan maintenance windows, troubleshoot application connectivity issues, and properly design network segmentation policies.

3. **Bandwidth Utilization Analysis**  
   Develop capabilities to break down network usage by application, protocol, and user groups to identify bandwidth hogs and optimization opportunities. This is crucial for Michael to manage network capacity, plan upgrades, identify anomalous usage patterns, and ensure critical business applications have sufficient network resources.

4. **Configuration Validation**  
   Build a system to identify mismatched network settings between communicating devices, such as MTU mismatches, duplex misconfigurations, and TCP parameter inconsistencies. This allows Michael to proactively identify configuration issues that cause subtle performance problems before they impact users or critical services.

5. **QoS (Quality of Service) Verification**  
   Create functionality to verify that priority traffic receives appropriate handling according to defined QoS policies. This feature is vital for Michael to ensure that critical applications like VoIP, video conferencing, and business transactions receive the necessary network resources even during periods of congestion.

## Technical Requirements

### Testability Requirements
- All components must be testable with enterprise network traffic datasets
- VLAN boundary analysis must be verifiable against known segmentation policies
- Service dependency mapping must be validated against reference network topologies
- Bandwidth analysis must be testable with synthetic traffic of known composition
- QoS verification must be testable against predetermined traffic prioritization expectations

### Performance Expectations
- Process at least 10GB of network traffic data in under 30 minutes
- Analyze complex network topologies with at least 1,000 nodes and 10,000 connections
- Generate service dependency maps for 100+ services in under 2 minutes
- Calculate bandwidth utilization metrics across multiple time intervals simultaneously
- Support incremental analysis of streaming data for near real-time monitoring

### Integration Points
- Import traffic from standard PCAP/PCAPNG and NetFlow/IPFIX data sources
- Export analysis in common formats (CSV, JSON, XML) for integration with other tools
- Import network topology and segmentation policy information
- Integration with SNMP and network device APIs for configuration validation
- Support for importing QoS policies from common network vendor formats

### Key Constraints
- Must handle distributed capture points across multiple network segments
- Analysis must work with incomplete visibility (sampled NetFlow, strategic capture points)
- Should function effectively with limited historical data retention
- Must scale to enterprise networks with 10,000+ endpoints
- Should operate without requiring installation of agents on endpoints

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Enterprise Network Analysis Framework should provide the following core functionality:

1. **Network Traffic Analysis Engine**
   - Parse and analyze network protocols from multiple data sources
   - Support for enterprise protocols (including routing, switching, and security protocols)
   - Correlation of traffic across multiple capture points
   - Statistical analysis with flexible time-series aggregation

2. **Segmentation and Security Analysis**
   - VLAN/subnet boundary crossing detection
   - Security zone policy compliance verification
   - Unauthorized access attempt identification
   - Micro-segmentation validation for zero-trust architectures

3. **Dependency and Topology Mapping**
   - Discovery of service communication patterns
   - Critical path identification for applications
   - Protocol usage analysis between services
   - Mapping of client-server and east-west traffic flows

4. **Performance and Capacity Analysis**
   - Protocol-level bandwidth consumption metrics
   - Application and user group usage patterns
   - Congestion detection and root cause analysis
   - Trend analysis for capacity planning

5. **Network Configuration Intelligence**
   - Identification of suboptimal network configurations
   - MTU, TCP window, and other parameter validation
   - QoS marking and queue allocation verification
   - Network optimization recommendations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of network protocol parsing and analysis
- Correctness of VLAN boundary detection
- Completeness of service dependency mapping
- Precision of bandwidth utilization calculations
- Effectiveness of configuration and QoS validation

### Critical User Scenarios
- Analyzing traffic patterns during a network slowdown incident
- Verifying that a security policy prevents inter-VLAN traffic as expected
- Mapping dependencies before migrating a critical application
- Identifying the source of unexpected bandwidth consumption
- Validating QoS implementation for VoIP traffic during network congestion

### Performance Benchmarks
- Process at least 10,000 packets per second on reference hardware
- Complete VLAN boundary analysis for a week of traffic in under 10 minutes
- Generate complete service dependency maps for 50+ services in under 60 seconds
- Calculate bandwidth utilization breakdowns with less than 1% margin of error
- Validate configuration settings across 100+ devices in under 5 minutes

### Edge Cases and Error Conditions
- Handling asymmetric routing where only one direction of traffic is visible
- Processing traffic with VLAN tags, Q-in-Q, and other encapsulation methods
- Analyzing traffic with multiple overlay technologies (VXLAN, GRE, IPsec)
- Dealing with incomplete or sampled traffic data (NetFlow)
- Handling multi-tier applications with complex communication patterns

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for VLAN boundary analysis
- 95% coverage for service dependency mapping
- 90% coverage for bandwidth utilization analysis
- 95% coverage for configuration and QoS validation

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

The Enterprise Network Analysis Framework implementation will be considered successful when:

1. It can accurately identify and report on traffic crossing VLAN boundaries with at least 95% accuracy
2. It successfully discovers and maps service dependencies with correct protocol identification
3. It provides bandwidth utilization breakdowns by application, protocol, and user group with less than 2% error margin
4. It identifies at least 90% of common network misconfigurations in test scenarios
5. It correctly verifies QoS implementation and identifies when priority traffic is not receiving proper treatment

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