# Wireless Protocol Analyzer for Complex Deployments

## Overview
A specialized network protocol analyzer designed for wireless network specialists to troubleshoot complex Wi-Fi deployments in challenging environments. The tool focuses on analyzing client roaming behavior, correlating signal quality with packet errors, examining wireless frame distributions, visualizing channel utilization, and analyzing client capability negotiations to optimize wireless network performance.

## Persona Description
Omar troubleshoots complex Wi-Fi deployments in challenging environments like hospitals and manufacturing facilities. He needs to analyze wireless protocol behavior and interference patterns affecting network performance.

## Key Requirements

1. **Wireless Handoff Analysis**
   - Implement comprehensive tracking and analysis of client roaming behavior between access points
   - Critical for Omar because poor handoff performance causes connectivity interruptions in mobile clients moving through facilities, affecting mission-critical applications in hospitals or manufacturing environments

2. **Signal Quality Correlation**
   - Create a system to correlate wireless signal metrics (RSSI, SNR, MCS) with packet error rates and retransmissions
   - Essential for Omar to identify the root causes of performance issues, distinguishing between RF interference problems, client limitations, and access point configuration issues

3. **Frame Subtype Analysis**
   - Develop detailed classification and statistical analysis of wireless frame types (control, management, data) and their distribution
   - Vital for Omar to understand protocol overhead, identify inefficient clients or access points, and optimize wireless network configuration for specific environments

4. **Channel Utilization Visualization**
   - Implement analytics to measure and visualize spectrum usage across frequency bands (2.4GHz, 5GHz, 6GHz)
   - Necessary for Omar to identify congested channels, optimize channel allocation, and maximize throughput in dense deployments where spectrum is a limited resource

5. **Client Capability Negotiation**
   - Create tools to analyze the negotiation of connection parameters between clients and access points
   - Critical for Omar to identify client devices with suboptimal capabilities that may be limiting overall network performance and to ensure proper matching of client capabilities with network configuration

## Technical Requirements

- **Testability Requirements**
  - All wireless analysis functions must be testable with captured 802.11 frame samples
  - Handoff analysis must be verifiable with simulated roaming scenarios
  - Signal correlation algorithms must be testable with synthetic data representing various RF conditions
  - All components must support deterministic testing without requiring actual wireless hardware

- **Performance Expectations**
  - Must process at least 100,000 wireless frames per minute on standard hardware
  - Channel utilization analysis must complete within 30 seconds for 1 hour of capture data
  - Client capability analysis must support batch processing of at least 1,000 clients concurrently
  - System must maintain consistent performance even with fragmented or malformed wireless frames

- **Integration Points**
  - Must support standard wireless capture formats (PCAP with Radiotap/PPI headers)
  - Should provide APIs for integration with wireless network management systems
  - Must support importing channel and regulatory domain configurations
  - Should interface with external RF spectrum analyzers when available

- **Key Constraints**
  - Analysis must work with encrypted wireless traffic (focusing on headers, not payload)
  - Must support all current 802.11 standards (a/b/g/n/ac/ax/be)
  - Should handle regional regulatory differences in channel availability
  - Must not require wireless transmission capabilities for analysis functions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a comprehensive library for wireless network protocol analysis with the following components:

1. **Roaming Analysis Engine**
   - Client mobility tracking across multiple access points
   - Timing analysis of handoff events and transitions
   - Identification of sticky client issues and roaming thresholds
   - Roaming efficiency scoring based on protocol standards

2. **RF Quality Correlation Framework**
   - Signal strength and quality metric extraction
   - Statistical correlation with packet errors and retransmissions
   - Environmental noise floor estimation and tracking
   - Rate adaptation analysis and optimization recommendations

3. **Frame Classification System**
   - Detailed parsing of 802.11 frame types and subtypes
   - Statistical analysis of protocol overhead
   - Management frame efficiency analysis
   - Control frame impact assessment

4. **Spectrum Utilization Analyzer**
   - Channel occupancy measurement across all supported bands
   - Co-channel and adjacent channel interference detection
   - Airtime fairness analysis between clients
   - Duty cycle tracking for periodic interferers

5. **Client Capability Analyzer**
   - Feature support detection from association frames
   - Capability negotiation tracking and optimization
   - Client fingerprinting and classification
   - Compatibility assessment between clients and infrastructure

## Testing Requirements

- **Key Functionalities to Verify**
  - Roaming analysis accurately tracks client transitions between access points
  - Signal quality correlation correctly identifies relationships between RF metrics and performance
  - Frame classification properly categorizes all 802.11 frame types and subtypes
  - Channel utilization analysis accurately measures spectrum usage
  - Client capability analysis correctly identifies supported and negotiated features

- **Critical User Scenarios**
  - Troubleshooting sporadic connectivity issues in a hospital with medical devices
  - Optimizing manufacturing floor coverage with multiple moving clients
  - Diagnosing interference issues in dense office environments
  - Planning channel allocation for maximum throughput
  - Identifying problematic legacy clients affecting overall network performance

- **Performance Benchmarks**
  - Process at least 100,000 wireless frames per minute
  - Complete full analysis of 24 hours of wireless captures within 10 minutes
  - Support concurrent analysis of at least 100 access points and 1,000 clients
  - Generate comprehensive wireless health reports in under 60 seconds
  - Maintain memory usage below 1GB during continuous operation

- **Edge Cases and Error Conditions**
  - Correct handling of non-standard vendor extensions
  - Proper operation with malformed wireless frames
  - Accurate analysis with mixed protocol environments (legacy and modern clients)
  - Robust operation with high noise environments and extreme packet loss
  - Graceful handling of partial captures or missing frames

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage across all modules
  - 100% coverage for frame parsing and classification functions
  - Comprehensive tests for all 802.11 standards
  - Performance tests verifying all specified benchmarks
  - Compatibility tests with all common wireless adapter types

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

1. Successfully identifies 95% of client roaming issues in test datasets
2. Establishes statistical correlation between signal quality and packet errors with at least 90% accuracy
3. Correctly classifies all 802.11 frame types and subtypes according to standards
4. Accurately measures channel utilization with less than 5% margin of error
5. Properly identifies client capabilities and negotiation parameters for all common device types
6. Processes high-volume wireless captures within performance parameters
7. Provides actionable recommendations that measurably improve wireless network performance
8. Supports analysis of complex multi-AP environments with hundreds of clients

## Project Setup

To set up the project environment:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install the project in development mode:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest tests/test_roaming_analyzer.py::test_handoff_detection
   ```

5. Run the analyzer on a packet capture:
   ```
   uv run python -m wireless_protocol_analyzer analyze --file hospital_wireless.pcap
   ```