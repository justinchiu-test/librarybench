# E-commerce Security Log Analysis Framework

## Overview
A specialized log analysis framework designed for security analysts monitoring e-commerce platforms that process sensitive payment data. The system focuses on real-time threat detection, compliance verification, session correlation, fraud detection, and geographic anomaly identification to protect customer data and financial transactions.

## Persona Description
Sophia monitors security logs for a high-traffic e-commerce platform processing sensitive payment data. She needs to identify potential security breaches and compliance issues across transaction processing systems in real-time.

## Key Requirements

1. **PCI DSS Compliance Reporting**
   - Automatically detect regulated data appearing in logs (credit card numbers, CVVs, etc.)
   - Generate compliance status reports organized by PCI DSS requirements
   - Track data exposure incidents with severity classification
   - Provide contextual links to relevant PCI DSS documentation
   - Support evidence collection for compliance audits
   
   *This feature is critical for Sophia because failing to maintain PCI DSS compliance puts customer financial data at risk and exposes the company to significant regulatory penalties and reputational damage.*

2. **Attack Pattern Recognition**
   - Classify suspicious activities using MITRE ATT&CK framework categories
   - Detect common web attack signatures (SQL injection, XSS, CSRF, etc.)
   - Identify account takeover attempts and credential stuffing attacks
   - Track attack progression across multiple systems
   - Calculate threat scores based on attack complexity and target sensitivity
   
   *This feature is essential as it helps Sophia identify sophisticated attack campaigns that may span multiple systems, allowing her to respond to threats based on established security frameworks rather than ad-hoc analysis.*

3. **User Session Correlation**
   - Link activities across multiple services to individual customer sessions
   - Track user journey through authentication, browsing, cart, and checkout processes
   - Maintain temporal session maps with event sequencing
   - Detect simultaneous sessions for the same user from different locations
   - Provide rapid session lookup by customer identifier, IP, or transaction ID
   
   *User session correlation is crucial because in e-commerce, security incidents often involve compromised accounts, and understanding the complete user journey helps Sophia distinguish between legitimate customer activity and malicious behavior.*

4. **Fraud Pattern Detection**
   - Identify anomalies based on historical transaction patterns
   - Score transactions for fraud likelihood based on multiple indicators
   - Detect account creation and purchasing patterns consistent with fraud rings
   - Track related transactions across different user accounts
   - Maintain a database of known fraud signatures
   
   *This feature is vital because fraudulent transactions can result in significant financial losses, chargebacks, and damaged customer relationships, making early detection of suspicious patterns a key responsibility for Sophia.*

5. **Geographic Access Visualization**
   - Highlight unusual login locations and traffic sources
   - Track access patterns by country, region, and IP address range
   - Identify VPN/proxy usage and TOR exit nodes
   - Compare current geographic access patterns with historical baselines
   - Generate alerts for unexpected location-based behaviors
   
   *Geographic visualization is essential since unusual access locations often indicate compromised accounts or attack attempts, and visual representation helps Sophia quickly identify access anomalies that would be difficult to detect in raw log data.*

## Technical Requirements

### Testability Requirements
- All detection rules must be testable with synthetic log data
- Compliance checks must be verified against PCI DSS requirements
- Pattern recognition algorithms need validation datasets with known attack signatures
- Session correlation must be tested across simulated multi-service flows
- Geographic detection requires test cases with diverse IP scenarios

### Performance Expectations
- Support real-time analysis of at least 5,000 transactions per minute
- Alert generation latency under 30 seconds for critical security events
- Support for pattern analysis across 90 days of historical data
- Search and correlation operations completed in under 5 seconds
- Efficient memory usage when processing high transaction volumes

### Integration Points
- Payment processor logging systems
- Web server and application logs
- Database audit logs
- Authentication service logs
- Network traffic logs
- IP geolocation services

### Key Constraints
- No storage of complete credit card numbers or authentication credentials
- Processing must prioritize security-relevant events
- Analysis must not impact production system performance
- No direct access to production databases
- All functionality accessible via well-defined Python APIs without UI components

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The E-commerce Security Log Analysis Framework must provide the following core capabilities:

1. **Log Collection and Normalization**
   - Ingest logs from diverse sources (web servers, applications, payment systems, databases)
   - Normalize log formats into a consistent internal structure
   - Identify and tag security-relevant events
   - Filter out noise and low-value log entries
   - Support both batch processing and real-time streaming

2. **Compliance Monitoring System**
   - Scan logs for presence of regulated data (PAN, CVV, personal information)
   - Map log events to PCI DSS control requirements
   - Generate compliance status reports
   - Track potential violations with impact assessment
   - Support evidence gathering for audit purposes

3. **Threat Detection Engine**
   - Apply MITRE ATT&CK classification to log events
   - Detect known attack signatures and patterns
   - Perform behavioral analysis for anomaly detection
   - Correlate events across different systems to identify attack campaigns
   - Calculate and assign threat scores to suspicious activities

4. **Session Analysis Subsystem**
   - Track user activities across the e-commerce platform
   - Maintain session timelines with all associated events
   - Provide rapid lookup and correlation between related sessions
   - Detect anomalous session behavior
   - Support reconstruction of user journeys for incident investigation

5. **Fraud Analysis Component**
   - Build and maintain user and transaction behavioral profiles
   - Detect deviations from established patterns
   - Identify relationships between seemingly unrelated transactions
   - Calculate fraud probability scores
   - Generate alerts for high-risk transactions

6. **Geographic Analysis Module**
   - Resolve IP addresses to geographic locations
   - Track and visualize access patterns by location
   - Detect location-based anomalies
   - Identify VPN, proxy, and anonymizer usage
   - Generate location-based risk assessments

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of regulated data in log streams
- Correct classification of attack patterns according to MITRE ATT&CK
- Proper correlation of user activities across multiple services
- Accurate identification of fraudulent transaction patterns
- Correct geographic resolution and anomaly detection

### Critical User Scenarios
- Detecting and responding to an SQL injection attack targeting customer records
- Identifying a compliance violation when credit card data appears in error logs
- Tracing a specific customer's journey through multiple services during an incident
- Recognizing coordinated fraud attempts across multiple accounts
- Identifying account takeover attempts from unusual geographic locations

### Performance Benchmarks
- Process and analyze at least 5,000 transactions per minute
- Generate alerts for critical security events within 30 seconds
- Complete session correlation queries in under 5 seconds
- Support analysis of at least 90 days of historical data
- Maintain system responsiveness during peak transaction periods

### Edge Cases and Error Conditions
- Handling of malformed or corrupted log entries
- Management of incomplete session data due to system failures
- Processing of logs during clock synchronization issues
- Handling of IP geolocation edge cases (proxies, VPNs, satellite connections)
- Correct operation during partial data availability from some subsystems

### Required Test Coverage Metrics
- Minimum 90% code coverage for security-critical components
- 100% coverage for PCI DSS compliance detection logic
- Comprehensive testing of attack signature detection
- Thorough validation of fraud scoring algorithms
- Full test coverage of session correlation mechanisms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Zero false negatives for PCI DSS compliance violations in test datasets
- Attack pattern recognition matches MITRE ATT&CK categorization with at least 90% accuracy
- Session correlation successfully links at least 99% of related events
- Fraud detection identifies at least 85% of known fraud patterns with fewer than 10% false positives
- Geographic anomaly detection correctly identifies 95% of unusual access patterns
- All operations complete within specified performance parameters
- Framework provides clear, actionable information through its APIs

To set up the development environment:
```
uv venv
source .venv/bin/activate
```