# Real-time Transaction Fraud Detection System

## Overview
A specialized data stream processing pipeline designed to analyze payment transactions in real-time, correlate events across multiple data streams, and identify potentially fraudulent activities with high accuracy and minimal false positives. The system employs adaptive detection mechanisms and provides detailed explanations for fraud determinations.

## Persona Description
Priya develops fraud detection systems that analyze payment transactions as they occur to identify suspicious patterns. Her primary goal is to correlate events across multiple data streams and quickly flag potentially fraudulent activities with minimal false positives.

## Key Requirements
1. **Multi-stream correlation with flexible joining conditions**: Implement a system that can dynamically join and correlate events across various data streams (transactions, login attempts, device information, location data) using configurable correlation rules. This capability is essential for identifying complex fraud patterns that span multiple systems and would be invisible when analyzing each stream in isolation.

2. **Adaptive rule engine that learns from analyst feedback**: Create a rules processing engine that can automatically adjust rule weights and thresholds based on feedback from fraud analysts about false positives and missed detections. This continuous learning mechanism ensures the system becomes more accurate over time and can adapt to evolving fraud tactics without manual reconfiguration.

3. **Risk scoring framework with explainable decision factors**: Develop a comprehensive risk scoring system that not only produces a numeric fraud probability score but also provides clear explanations of which factors contributed to the score and why. This explainability is critical for regulatory compliance, analyst investigations, and building customer trust when legitimate transactions are declined.

4. **Historical context integration for establishing behavioral baselines**: Build mechanisms to dynamically compare current transaction patterns against historical behaviors for the same customer, merchant, or payment instrument to identify anomalous activities. This behavioral profiling is crucial for detecting account takeovers and subtle fraud that might appear normal in isolation but deviates from established patterns.

5. **Case management system for tracking investigation outcomes**: Implement a framework for organizing flagged transactions into investigation cases, tracking analyst decisions, and feeding those outcomes back into the detection system. This closed-loop approach ensures continuous improvement and provides audit trails for compliance and performance measurement.

## Technical Requirements
- **Testability Requirements**:
  - Must support simulation with historical fraud scenarios and synthetic data
  - Needs reproducible testing environments with controlled data inputs
  - Requires isolation of rule performance metrics for optimization
  - Must support A/B testing of rule modifications
  - Needs automated regression testing against known fraud patterns

- **Performance Expectations**:
  - Ability to process at least 10,000 transactions per second
  - Maximum latency of 200ms for end-to-end fraud scoring
  - Support for at least 100 concurrent fraud rules with complex logic
  - False positive rate below 3% for high-risk scores
  - Capability to store and query at least 2 years of historical customer data

- **Integration Points**:
  - Payment processing systems and gateways
  - Customer identity and authentication systems
  - Device intelligence and fingerprinting services
  - Geolocation and IP intelligence providers
  - Case management and workflow systems for fraud analysts

- **Key Constraints**:
  - Must comply with PCI-DSS and relevant data privacy regulations
  - System must operate with minimal impact on customer experience
  - Implementation must be audit-friendly with comprehensive logging
  - Solution must be explainable for regulatory and customer service purposes
  - All processing must complete within the payment authorization window

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a framework for real-time transaction fraud detection that:

1. Ingests data from multiple sources including:
   - Payment transaction details
   - Customer account activities
   - Authentication events
   - Device and location information
2. Normalizes and enriches incoming data with relevant context
3. Implements a flexible stream joining and correlation engine
4. Processes transactions through multi-layered detection:
   - Rule-based filters for known fraud patterns
   - Behavioral analysis using historical profiles
   - Anomaly detection for unusual patterns
   - Risk scoring with factor attribution
5. Provides feedback mechanisms for analyst decisions
6. Adapts detection models based on confirmed outcomes
7. Organizes suspicious activities into investigation cases
8. Maintains audit trails and performance metrics

The implementation should emphasize accuracy, speed, explainability, and continuous improvement through analyst feedback loops.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct implementation of multi-stream correlation
  - Proper functioning of the adaptive rule engine
  - Accuracy of risk scoring and factor attribution
  - Effective use of historical context in decision making
  - Appropriate case management and feedback integration

- **Critical User Scenarios**:
  - Detection of account takeover fraud through behavioral changes
  - Identification of card testing attacks with distributed low-value transactions
  - Recognition of synthetic identity fraud through pattern analysis
  - Detection of unusual spending patterns compared to customer history
  - Handling of legitimate but unusual transactions with minimal friction

- **Performance Benchmarks**:
  - Processing latency under 200ms per transaction at full load
  - Throughput of 10,000+ transactions per second
  - Rule evaluation time under 50ms for 100+ concurrent rules
  - Less than 3% false positive rate on historical fraud scenarios
  - Detection rate of at least 85% for known fraud patterns

- **Edge Cases and Error Conditions**:
  - Handling of incomplete transaction data
  - Processing behavior during data feed interruptions
  - Response to sudden transaction volume spikes
  - Performance under degraded historical data access
  - Behavior with conflicting rule evaluations

- **Required Test Coverage Metrics**:
  - 100% coverage of core fraud detection logic
  - >90% line coverage for all production code
  - 100% coverage of decision paths in risk scoring
  - Integration tests for all data stream correlation capabilities
  - Comprehensive tests for all supported rule types

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
A successful implementation will demonstrate:

1. Accurate detection of fraudulent transactions with minimal false positives
2. Effective correlation of events across multiple data streams
3. Adaptive learning from analyst feedback to improve detection accuracy
4. Clear explanation of risk factors contributing to fraud scores
5. Intelligent use of historical behavior patterns for anomaly detection
6. Efficient organization of fraud cases for investigation
7. Comprehensive test coverage with all tests passing

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

To setup the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```