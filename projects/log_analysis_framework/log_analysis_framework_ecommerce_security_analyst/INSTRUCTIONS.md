# E-commerce Security Log Analysis Framework

A specialized log analysis framework designed for security analysts monitoring e-commerce platforms processing sensitive payment data.

## Overview

This project implements a security-focused log analysis system tailored for high-traffic e-commerce environments. It provides real-time monitoring and analysis capabilities for detecting potential security breaches, compliance violations, and suspicious user activities across transaction processing systems.

## Persona Description

Sophia monitors security logs for a high-traffic e-commerce platform processing sensitive payment data. She needs to identify potential security breaches and compliance issues across transaction processing systems in real-time.

## Key Requirements

1. **PCI DSS Compliance Reporting**
   - Implement automatic detection of regulated data appearing in logs
   - Critical for Sophia to maintain compliance with payment card industry standards and prevent data leakage
   - Must identify patterns indicating presence of credit card numbers, CVV codes, or other protected payment data in logs
   - Should generate compliance reports suitable for audits with evidence of monitoring

2. **Attack Pattern Recognition**
   - Develop detection capabilities using MITRE ATT&CK framework classifications
   - Essential for Sophia to categorize and understand attack vectors targeting the e-commerce platform
   - Should detect common web attack patterns such as SQL injection, XSS, CSRF, and more sophisticated patterns
   - Must map detected patterns to MITRE ATT&CK tactics and techniques for standardized reporting

3. **User Session Correlation**
   - Create functionality to link activities across multiple services to individual customers
   - Necessary for Sophia to trace user journeys and identify suspicious behavior spanning different system components
   - Should reconstruct complete user sessions from login through checkout across microservices
   - Must handle anonymous sessions and transitions to authenticated states

4. **Fraud Pattern Detection**
   - Implement anomaly scoring based on historical transaction patterns
   - Important for Sophia to identify potential fraudulent transactions before they're completed
   - Should analyze patterns like unusual purchase amounts, account changes before purchases, or atypical shipping destinations
   - Must score transactions based on deviation from typical behavior for that user/IP/device

5. **Geographic Access Visualization**
   - Build capability to highlight unusual login locations and traffic sources
   - Vital for Sophia to quickly identify geographic anomalies indicating account takeover
   - Should detect impossible travel scenarios (login from different countries in impossibly short timeframes)
   - Must visualize traffic patterns and highlight unusual origin points

## Technical Requirements

### Testability Requirements
- All components must be testable with pytest using appropriate mocks and fixtures
- Tests must validate detection accuracy using known attack signature samples
- Must include comprehensive tests for PCI DSS pattern matching with test data that doesn't include actual PII
- Test coverage must exceed 90% for security-critical detection logic
- Performance tests must validate real-time processing capabilities

### Performance Expectations
- Must process high-volume transaction logs (5,000+ transactions per minute) with <5 second alert time
- Should handle peak holiday traffic surges (10x normal volume) without degradation
- Pattern matching algorithms should optimize for low false-positive rates (<1%) while maintaining high detection rates
- Geographic analysis should complete within 3 seconds even for complex global traffic patterns

### Integration Points
- Integration with e-commerce transaction processing systems (payment gateways, checkout services)
- Compatibility with web server logs (Apache, Nginx), application logs, and WAF logs
- Integration with IP geolocation databases for geographic analysis
- Optional integration with SIEM systems via standard formats (CEF, LEEF, Syslog)

### Key Constraints
- Must never store actual PCI data, even temporarily, while processing logs
- Should operate without imposing performance penalties on production e-commerce systems
- Implementation must be compliance-friendly (auditable, documented, secure)
- Should have minimal false positives that could lead to unnecessary transaction blocking

## Core Functionality

The system must implement these core capabilities:

1. **Secure Log Collection**
   - Collect logs from web servers, application servers, payment processors, and databases
   - Filter sensitive data before storage when possible
   - Secure transport and storage of log data
   - Validate log integrity and detect tampering

2. **PCI DSS Pattern Monitoring**
   - Detect PCI regulated data patterns in logs
   - Identify potential data leakage in application outputs
   - Generate compliance reports with evidence
   - Alert on potential compliance violations

3. **Security Analysis Engine**
   - Detect attack signatures across multiple log sources
   - Map detected activities to MITRE ATT&CK framework
   - Score events by severity and confidence
   - Correlate events into security incidents

4. **User Session Tracker**
   - Reconstruct user journeys across distributed systems
   - Link anonymous and authenticated activities
   - Detect session anomalies (hijacking, replay)
   - Establish baselines for normal user behavior

5. **Fraud Detection System**
   - Analyze transaction patterns for anomalies
   - Score transactions by risk level
   - Detect account takeovers and suspicious changes
   - Identify coordinated fraud campaigns across users

## Testing Requirements

### Key Functionalities to Verify

- **PCI Pattern Detection**: Validate accurate detection of PCI data patterns without false positives
- **Attack Recognition**: Verify correct identification of common attack patterns against e-commerce systems
- **Session Correlation**: Ensure accurate tracking of user activities across distributed services
- **Fraud Detection**: Confirm detection of anomalous transaction patterns with minimal false positives
- **Geographic Analysis**: Validate accurate identification of unusual access locations and impossible travel

### Critical User Scenarios

- Detecting and responding to active SQL injection attempts targeting product search
- Identifying potential data leakage of credit card information in application logs
- Tracking suspicious user behavior from login through checkout across services
- Analyzing a spike in failed transactions from a specific geographic region
- Investigating account takeover attempts with credential stuffing

### Performance Benchmarks

- Process logs from 10,000 concurrent active users with <5 second detection latency
- Handle 5,000+ transactions per minute with real-time fraud scoring
- Complete geographic analysis for 1,000+ simultaneous logins in under 3 seconds
- Analyze 30 days of historical transaction data for a single user in under 10 seconds
- Generate PCI DSS compliance reports covering millions of transactions in under 5 minutes

### Edge Cases and Error Handling

- Handle partial log data from services during outages without false positives
- Process logs with timezone inconsistencies across international services
- Manage false positives for legitimate users with unusual but non-fraudulent behavior
- Handle new attack patterns not matching existing signatures
- Correctly process logs during dramatic traffic spikes (10x normal volume)

### Test Coverage Requirements

- 100% coverage for PCI data pattern detection logic
- 95% coverage for attack signature detection
- 90% coverage for user session correlation
- 90% coverage for fraud pattern analysis
- 90% overall code coverage

## Success Criteria

The implementation meets Sophia's needs when it can:

1. Automatically detect and alert on PCI DSS compliance violations with >99% accuracy
2. Correctly identify and classify security attacks using MITRE ATT&CK framework with >90% accuracy
3. Successfully correlate user activities across at least 5 different microservices into coherent sessions
4. Detect fraudulent transaction patterns with >95% accuracy and <1% false positives
5. Visualize and alert on geographic access anomalies within 5 seconds of occurrence
6. Process peak holiday traffic volumes without performance degradation
7. Reduce time to detection for security incidents by at least 70%

## Getting Started

To set up your development environment and start working on this project:

1. Initialize a new Python library project using uv:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run specific tests:
   ```
   uv run pytest tests/test_pci_detection.py
   ```

5. Run your code:
   ```
   uv run python examples/analyze_transaction_logs.py
   ```

Remember that all functionality should be implemented as importable Python modules with well-defined APIs, not as user-facing applications.