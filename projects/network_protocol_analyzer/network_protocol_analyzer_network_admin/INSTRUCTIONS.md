# NetScope - Enterprise Network Segmentation and Performance Analyzer

## Overview
A specialized network protocol analyzer designed for enterprise network administrators to verify network segmentation, map service dependencies, analyze bandwidth utilization, validate device configurations, and ensure quality of service across complex corporate networks.

## Persona Description
Michael manages network infrastructure for a large corporation with complex connectivity requirements. He needs to troubleshoot performance bottlenecks, identify misconfigured services, and ensure proper segmentation between network zones.

## Key Requirements
1. **VLAN boundary analysis verifying traffic segregation between network segments**
   - Implement detection and verification of VLAN tag integrity and proper segmentation
   - Create analytical tools to identify unauthorized cross-segment traffic
   - Include reporting on segmentation effectiveness and potential security risks from improper boundaries
   - Develop methods to validate that traffic stays within expected network zones

2. **Service dependency mapping showing which systems communicate with each other**
   - Create functionality to automatically discover and map communication patterns between endpoints
   - Implement visualization capabilities for service relationships and dependencies
   - Include change detection to identify new or modified service connections
   - Develop methods to distinguish between regular and anomalous service communications

3. **Bandwidth utilization breakdown by application, protocol, and user groups**
   - Implement traffic classification to categorize network usage by application type
   - Create analysis tools to aggregate bandwidth consumption by protocol type and business unit
   - Include temporal pattern detection to identify peak usage periods and trends
   - Develop prioritization recommendations based on business-critical services

4. **Configuration validation identifying mismatched network settings between devices**
   - Develop protocol analysis capability to identify inconsistent network configurations
   - Create functionality to detect MTU mismatches, duplex disagreements, and routing inconsistencies
   - Include identification of suboptimal TCP window sizes and other protocol-level configurations
   - Implement configuration baseline comparison for network device families

5. **QoS (Quality of Service) verification ensuring priority traffic receives appropriate handling**
   - Implement DSCP/ToS field analysis to verify proper packet prioritization
   - Create measurement tools for analyzing latency and jitter for high-priority traffic classes
   - Include verification of bandwidth reservation effectiveness for critical applications
   - Develop methods to detect QoS misconfiguration and policy violations

## Technical Requirements
- **Testability Requirements**
  - All components must have comprehensive unit tests with at least 90% code coverage
  - Include simulation capabilities for testing against various network topologies
  - Support capture replay for consistent testing across environments
  - Implement configuration mocking to test against various network device settings

- **Performance Expectations**
  - Process and analyze traffic at rates of at least 100,000 packets per second
  - Analyze enterprise-scale network captures (10+ GB) without memory exhaustion
  - Generate comprehensive reports within minutes even for large networks
  - Support continuous monitoring with minimal impact on network performance

- **Integration Points**
  - Integration with packet capture libraries for enterprise-grade network monitoring
  - Export formats compatible with network documentation and CMDB systems
  - API endpoints for integration with network monitoring and management platforms
  - Command-line interface for integration with automation scripts and tools

- **Key Constraints**
  - Implementation must be in Python with minimal external dependencies
  - Analysis must function with only packet data (no direct device access required)
  - Solution must handle multiple simultaneous VLANs and routing domains
  - No user interface components should be implemented; focus solely on API and library functionality
  - All functionality must be accessible programmatically for integration with existing tools

## Core Functionality
The core functionality includes network traffic analysis with special focus on segmentation verification, service discovery and dependency mapping, bandwidth utilization analysis, configuration validation, and QoS verification.

The system will parse network packets across multiple protocols with particular attention to VLAN tags, IP subnets, routing information, and QoS markings. It will maintain state to track conversations between endpoints, build service dependency maps, and identify traffic patterns associated with specific applications or business functions.

The implementation should provide detailed reporting on network segmentation effectiveness, bandwidth utilization patterns, configuration inconsistencies, and QoS effectiveness. Reports should be exportable in machine-readable formats for integration with other enterprise systems.

For configuration validation, the system should infer device configurations from observed traffic patterns and identify potential misconfigurations without requiring direct device access. Similarly, QoS verification should assess whether traffic marked for prioritization is actually receiving preferential treatment through the network.

## Testing Requirements
- **Key Functionalities to Verify**
  - Accurate detection of VLAN boundaries and cross-segment traffic
  - Reliable service dependency discovery and mapping
  - Precise bandwidth utilization measurement and categorization
  - Effective identification of network configuration mismatches
  - Accurate verification of QoS effectiveness and policy compliance

- **Critical User Scenarios**
  - Verifying segmentation after network reconfiguration
  - Mapping service dependencies before major infrastructure changes
  - Analyzing bandwidth utilization during peak business hours
  - Identifying the sources of intermittent network performance issues
  - Verifying QoS effectiveness for real-time applications like VoIP

- **Performance Benchmarks**
  - Complete segmentation analysis of a 24-hour traffic capture within 15 minutes
  - Generate comprehensive service dependency maps for networks with 1000+ endpoints within 30 minutes
  - Process and categorize bandwidth utilization at line rate for 1Gbps networks
  - Complete configuration validation checks within 5 minutes for enterprise-scale networks

- **Edge Cases and Error Conditions**
  - Handling incomplete capture data with missing packets
  - Analyzing traffic with non-standard protocol implementations
  - Processing traffic from overlapping IP spaces in different VLANs
  - Dealing with tunneled or encapsulated traffic
  - Managing analysis across multiple capture points with time synchronization issues

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage for all analysis components
  - 100% coverage of public APIs
  - Comprehensive protocol support verification
  - Performance testing under various network load conditions

## Success Criteria
The implementation will be considered successful if:

1. It accurately identifies at least 95% of improper cross-segment traffic in test datasets
2. Service dependency maps correctly identify all significant service relationships
3. Bandwidth utilization analysis correctly categorizes at least 90% of network traffic by application
4. Configuration validation identifies at least 90% of common configuration mismatches
5. QoS verification correctly identifies whether priority traffic is receiving preferential treatment
6. All analyses complete within the specified performance targets
7. All functionality is accessible programmatically through well-documented APIs
8. The system can process enterprise-scale networks without performance degradation
9. All tests pass consistently across different environments

## Setting Up the Project

To set up the project environment, follow these steps:

1. Initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run Python scripts:
   ```
   uv run python script.py
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Run specific tests:
   ```
   uv run pytest tests/test_specific.py::test_function_name
   ```