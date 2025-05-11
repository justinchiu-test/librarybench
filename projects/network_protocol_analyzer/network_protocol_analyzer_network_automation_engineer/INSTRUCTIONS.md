# Network Automation Analysis Framework

## Overview
A specialized network protocol analysis library designed for network automation engineers to verify the behavior of automated network configuration changes, providing before/after comparisons, configuration validation, intent verification, failure scenario simulation, and API-driven integration with automation pipelines.

## Persona Description
Priya develops automation systems for large network infrastructures. She needs to understand and verify the behavior of automated network configuration changes and ensure they produce the expected traffic patterns.

## Key Requirements

1. **Before/After Comparison System**  
   Create a module that visualizes and analyzes network behavior changes following automated updates. This is critical for Priya because it allows her to verify that automation changes produce the expected traffic patterns and network behaviors, providing clear evidence that automated configuration changes achieved their intended network state without unintended consequences.

2. **Configuration Change Validation**  
   Implement functionality to correlate specific device configuration changes with resulting traffic pattern alterations. This feature is essential for Priya to establish clear causality between automation-driven configuration changes and their network effects, helping debug automation scripts, identify configuration parameters with the most impact, and verify that changes propagate correctly.

3. **Intent Verification System**  
   Develop capabilities to confirm that automation achieves desired network behavior based on predefined intent specifications. This is crucial for Priya because intent-based networking requires verification that high-level business intent correctly translates into proper network behavior, allowing her to validate that automation correctly implements complex policy requirements.

4. **Failure Scenario Simulation**  
   Build a system to predict the traffic impact of potential automation errors without affecting production networks. This allows Priya to safely test automation failure modes, understand the potential blast radius of failed changes, and develop more robust fallback mechanisms and validation checks that can prevent outages from automation errors.

5. **API-driven Analysis Integration**  
   Create functionality to integrate network analysis directly into automation pipelines for continuous monitoring. This feature is vital for Priya to build self-healing and self-validating automation systems that can verify their own effectiveness, rollback unsuccessful changes, and provide continuous validation that the network maintains its desired state across multiple change cycles.

## Technical Requirements

### Testability Requirements
- All components must be testable with before/after network traffic datasets
- Configuration validation must be verifiable against known device changes
- Intent verification must be testable against formal intent specifications
- Failure simulations must produce deterministic and reproducible results
- API integrations must be testable with mocked automation pipelines

### Performance Expectations
- Complete before/after analysis of major network changes in under 5 minutes
- Process configuration validation across 100+ network devices in parallel
- Verify intent compliance within 60 seconds of configuration changes
- Simulate failure impacts for complex networks (1000+ devices) in under 10 minutes
- Support continuous analysis at least every 5 minutes for large networks

### Integration Points
- Import traffic from standard PCAP/PCAPNG files, NetFlow, and IPFIX
- Support for reading configuration from common network device formats
- Integration with automation systems via REST APIs
- Import intent models from YANG, TOSCA, or custom intent formats
- Webhook support for event-driven analysis triggers

### Key Constraints
- Must operate safely alongside production automation systems
- Should minimize performance impact on automation pipelines
- Must handle multi-vendor network environments
- Should support both imperative and declarative automation approaches
- Must operate with least-privilege access to network devices

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Network Automation Analysis Framework should provide the following core functionality:

1. **Network Change Impact Analysis**
   - Compare traffic patterns before and after configuration changes
   - Measure and highlight statistically significant changes
   - Track convergence times and stability after changes
   - Identify unexpected behavior changes across protocols

2. **Configuration to Behavior Correlation**
   - Link specific configuration parameters to observable network effects
   - Analyze the propagation of changes through the network
   - Track configuration state across device reloads
   - Measure configuration compliance with templates

3. **Intent-based Verification**
   - Validate that network behavior matches defined intent
   - Translate high-level policy to expected traffic patterns
   - Detect policy violations in observed traffic
   - Measure the degree of intent fulfillment

4. **Failure Analysis and Prediction**
   - Simulate traffic paths during partial failures
   - Model impact of misconfiguration scenarios
   - Analyze redundancy effectiveness
   - Recommend failure detection improvements

5. **Automation Integration Services**
   - Provide programmable interfaces for continuous validation
   - Support event-driven analysis workflows
   - Generate machine-readable verification results
   - Enable closed-loop validation and remediation

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of before/after traffic pattern comparison
- Correctness of configuration change correlation
- Effectiveness of intent verification
- Reliability of failure scenario predictions
- Robustness of API integration

### Critical User Scenarios
- Validating traffic flows after an automated BGP policy change
- Correlating ACL modifications with traffic filtering behavior
- Verifying that QoS implementations match service level intents
- Predicting the impact of automation errors in a route reflector configuration
- Integrating analysis into a CI/CD pipeline for network changes

### Performance Benchmarks
- Complete before/after analysis of routing table changes in under 2 minutes
- Correlate configuration changes to traffic impacts with at least 90% accuracy
- Verify intent compliance across 50 policy rules in under 30 seconds
- Simulate failure scenarios with 95% accuracy compared to actual failures
- Handle at least 10 concurrent API-driven analysis requests

### Edge Cases and Error Conditions
- Handling partial or incomplete configuration changes
- Processing network changes during transitional states
- Analyzing unexpected protocol interactions after changes
- Dealing with vendor-specific behavior variations
- Supporting brownfield environments with undocumented configurations

### Required Test Coverage Metrics
- Minimum 90% code coverage for core functionality
- 95% coverage for before/after comparison
- 95% coverage for configuration change validation
- 90% coverage for intent verification
- 95% coverage for API integration components

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

The Network Automation Analysis Framework implementation will be considered successful when:

1. It accurately identifies and visualizes network behavior changes after automated configuration updates
2. It successfully correlates specific configuration parameters with their network behavior impacts
3. It correctly verifies that network behavior matches defined intent specifications
4. It predicts failure impacts with at least 90% accuracy compared to actual failure tests
5. It integrates smoothly with automation pipelines through well-defined APIs

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