# Wireless Network Protocol Analysis Framework

## Overview
A specialized network protocol analysis library for wireless network specialists to analyze Wi-Fi deployments, focusing on client roaming behavior, signal quality correlations, frame type analysis, channel utilization patterns, and client capability negotiation to optimize wireless networks in challenging environments.

## Persona Description
Omar troubleshoots complex Wi-Fi deployments in challenging environments like hospitals and manufacturing facilities. He needs to analyze wireless protocol behavior and interference patterns affecting network performance.

## Key Requirements

1. **Wireless Handoff Analysis System**  
   Create a module that tracks and analyzes client roaming behavior between access points, including timing, triggers, and success rates. This is critical for Omar because seamless client handoffs are essential in environments like hospitals where medical devices and staff must maintain reliable connectivity while moving throughout the facility, and poor roaming implementations cause dropped connections and service disruptions.

2. **Signal Quality Correlation Engine**  
   Implement functionality to link packet errors and retransmissions with wireless interference and signal quality metrics. This feature is essential for Omar to identify the root causes of wireless performance problems in noisy RF environments like manufacturing facilities with heavy machinery, allowing him to distinguish between protocol issues, RF interference, and client-specific problems.

3. **Frame Subtype Analysis**  
   Develop capabilities to categorize and analyze the distribution of control, management, and data frames across the wireless network. This is crucial for Omar because an imbalanced frame distribution can indicate network health issues, inefficient configurations, or problematic clients, and understanding the protocol overhead helps optimize wireless network capacity in high-density environments.

4. **Channel Utilization Visualization**  
   Build a system to identify congestion and interference patterns across different frequency bands and channels. This allows Omar to optimize channel assignments, detect co-channel interference, and understand utilization patterns that cause performance problems in crowded wireless environments, especially when working with limited clean spectrum availability.

5. **Client Capability Negotiation Analysis**  
   Create functionality to examine the process of capability selection and parameter negotiation between clients and access points. This feature is vital for Omar to identify clients that aren't using optimal connection parameters or falling back to legacy rates, which helps him troubleshoot performance disparities between device types and ensure all devices operate at their maximum potential.

## Technical Requirements

### Testability Requirements
- All components must be testable with wireless capture files (PCAP with radiotap headers)
- Roaming analysis must be verifiable against known roaming events
- Signal correlation must be testable with RF measurement data
- Frame analysis must be validated against known frame distributions
- Client capability analysis must be verifiable against device specifications

### Performance Expectations
- Process at least 1GB of wireless capture data in under 10 minutes
- Track roaming for at least 1,000 clients across 100 access points
- Correlate signal metrics with at least 95% accuracy compared to specialized tools
- Analyze frame distribution across 50+ channels simultaneously
- Support 802.11 amendments including a/b/g/n/ac/ax (Wi-Fi 6) protocol analysis

### Integration Points
- Import from wireless packet captures with radiotap/PPI headers
- Support for importing access point location data and floor plans
- Integration with external RF spectrum analysis data when available
- Export findings in formats compatible with wireless survey tools
- API for correlation with WLAN controller statistics

### Key Constraints
- Must handle encrypted wireless traffic (WPA2/WPA3)
- Should work with captures from multiple, distributed sensors
- Must process vendor-specific Information Elements and capabilities
- Should handle captures from different chipsets with varying radiotap fields
- Must support analysis of wireless networks using multiple frequency bands

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Wireless Network Protocol Analysis Framework should provide the following core functionality:

1. **802.11 Protocol Analysis Engine**
   - Parse and decode wireless frames and their subtypes
   - Extract and interpret radiotap/PPI headers for RF metrics
   - Analyze protocol behaviors across different amendments
   - Support for wireless security protocol analysis

2. **Roaming and Mobility Analysis**
   - Track client associations across multiple access points
   - Analyze roaming decisions and their triggers
   - Measure roaming delay and success rates
   - Identify sticky client behavior and roaming failures

3. **RF Quality and Interference Assessment**
   - Correlate signal metrics with transmission errors
   - Analyze retry rates and their relationship to signal quality
   - Track SNR (Signal-to-Noise Ratio) impact on data rates
   - Identify patterns indicating external interference

4. **Spectrum and Channel Analysis**
   - Measure airtime utilization across channels
   - Identify co-channel and adjacent channel interference
   - Analyze frequency band usage patterns
   - Evaluate channel bonding effectiveness

5. **Client and AP Capability Analysis**
   - Decode and analyze supported data rates and capabilities
   - Track negotiated connection parameters
   - Identify suboptimal feature negotiation
   - Compare actual versus potential performance

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of wireless protocol decoding and analysis
- Correctness of roaming event detection and analysis
- Precision of signal quality correlation with packet errors
- Completeness of frame categorization and statistics
- Effectiveness of client capability analysis

### Critical User Scenarios
- Analyzing roaming patterns for medical devices in a hospital deployment
- Correlating interference patterns with packet loss in a manufacturing facility
- Identifying excessive management frame overhead in a high-density environment
- Mapping channel utilization across a multi-floor office building
- Troubleshooting why specific client devices negotiate lower data rates

### Performance Benchmarks
- Process at least 10,000 wireless frames per second on reference hardware
- Complete roaming analysis for 24 hours of traffic in under 15 minutes
- Generate signal correlation metrics with less than 5% deviation from specialized tools
- Analyze frame distribution across all channels in under 30 seconds
- Process client capability negotiation for 500 clients in under 60 seconds

### Edge Cases and Error Conditions
- Handling captures with incomplete roaming sequences
- Processing mixed-mode networks (e.g., 802.11ac and 802.11ax)
- Analyzing networks with multiple BSSIDs per radio
- Dealing with vendor-specific extensions and non-standard behaviors
- Supporting mesh wireless deployments and repeated SSIDs

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for wireless handoff analysis
- 95% coverage for signal quality correlation
- 90% coverage for frame subtype analysis
- 95% coverage for client capability analysis

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

The Wireless Network Protocol Analysis Framework implementation will be considered successful when:

1. It accurately detects and analyzes at least 95% of roaming events in test captures
2. It successfully correlates signal quality metrics with packet errors with at least 90% accuracy
3. It correctly categorizes frame subtypes and provides meaningful distribution statistics
4. It accurately measures channel utilization across different bands and channels
5. It properly analyzes client capability negotiation and identifies suboptimal connections

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