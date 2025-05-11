# Medical Device Monitoring Stream Processing System

## Overview
A specialized data stream processing framework designed to reliably collect, analyze, and monitor vital sign data from medical devices in both hospital and remote patient settings. The system ensures continuous delivery of critical patient data, detects medically significant events, and maintains compliance with healthcare regulations and privacy requirements.

## Persona Description
Sophia develops patient monitoring systems that process vital sign data from medical devices in both hospital and remote settings. Her primary goal is to ensure reliable delivery of critical patient data while detecting medically significant events that require intervention.

## Key Requirements
1. **Medical device protocol support with standards compliance**: Implement a comprehensive adapter framework supporting diverse medical device protocols and standards (HL7, FHIR, DICOM, proprietary device protocols) with full regulatory compliance. This capability is essential for interfacing with the heterogeneous medical device ecosystem found in healthcare environments, ensuring accurate data collection from bedside monitors, wearables, and implantable devices.

2. **Patient-specific baseline calibration and alert thresholds**: Create a system that establishes and continuously updates individualized baseline normal ranges for each patient's physiological parameters, accounting for demographics, medical history, and condition progression. This personalization is critical for reducing false alarms while ensuring true clinical deterioration is detected, addressing the alarm fatigue problem in healthcare.

3. **Signal quality assessment with artifact rejection**: Develop algorithms that continuously evaluate the quality of incoming vital sign data, automatically identifying and filtering artifactual signals caused by patient movement, device disconnection, or interference. This signal validation is vital for maintaining data integrity and preventing erroneous clinical decisions based on corrupted readings.

4. **Medical event pattern recognition with severity classification**: Implement a pattern recognition framework that detects clinically significant events (arrhythmias, desaturations, respiratory distress patterns) from multi-parameter vital sign data and classifies them by severity level. This detection capability enables timely clinical intervention for truly significant events while appropriately prioritizing alerts.

5. **Compliance-focused audit logging with privacy controls**: Design a comprehensive audit logging system that tracks all data access, processing, and clinical alerting while enforcing appropriate privacy protections and data visibility controls. This auditing is mandatory for regulatory compliance (HIPAA, GDPR) and provides critical documentation for clinical decision review and quality assurance.

## Technical Requirements
- **Testability Requirements**:
  - Must support validation with annotated clinical datasets
  - Needs reproducible testing with synthetic patient data
  - Requires certification testing for medical device integration
  - Must support verification of alert generation accuracy
  - Needs compliance validation for regulatory requirements

- **Performance Expectations**:
  - Support for at least 1,000 simultaneously monitored patients
  - Maximum alerting latency of 5 seconds for critical events
  - Continuous processing of at least 20 parameters per patient at 1Hz
  - High-resolution ECG processing at 250Hz per monitored lead
  - System availability of 99.99% with no scheduled downtime

- **Integration Points**:
  - Medical device data streams (bedside monitors, wearables, implantables)
  - Electronic Health Record (EHR) systems
  - Clinical decision support systems
  - Alert management and notification platforms
  - Hospital information systems
  - Remote patient monitoring platforms

- **Key Constraints**:
  - Must comply with relevant healthcare regulations (HIPAA, GDPR, FDA)
  - Implementation must maintain patient data privacy and security
  - System must operate without performance degradation 24/7/365
  - Processing must prioritize patient safety over performance optimization
  - All components must meet healthcare reliability standards

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a framework for medical device data processing that:

1. Ingests data from diverse medical devices via multiple protocols
2. Validates and normalizes vital sign data for consistency
3. Establishes patient-specific baseline parameters and thresholds
4. Continuously monitors data quality and rejects artifacts
5. Processes multi-parameter data to detect significant clinical events
6. Classifies detected events by medical severity and urgency
7. Generates appropriate alerts for clinical intervention
8. Maintains comprehensive audit trails with privacy controls
9. Scales efficiently from individual patient to hospital-wide monitoring
10. Ensures compliance with healthcare standards and regulations

The implementation should emphasize patient safety, data accuracy, system reliability, and regulatory compliance while providing the flexibility to adapt to diverse healthcare environments.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct implementation of medical device protocols
  - Accuracy of patient-specific baseline calibration
  - Effectiveness of signal quality assessment and artifact rejection
  - Reliability of medical event detection and classification
  - Completeness of compliance logging and privacy controls

- **Critical User Scenarios**:
  - Continuous monitoring of critical care patients with multiple devices
  - Remote monitoring of chronic condition patients at home
  - Detection of gradual patient deterioration requiring intervention
  - Handling of noisy signals during patient movement or transport
  - Response to sudden acute events requiring immediate attention

- **Performance Benchmarks**:
  - Alert generation within 5 seconds of clinical event onset
  - False positive rate below 5% for critical alerts
  - False negative rate below 1% for life-threatening conditions
  - Processing capacity for 1,000+ simultaneous patients
  - System uptime of 99.99% with redundant processing paths

- **Edge Cases and Error Conditions**:
  - Handling of medical device disconnection or failure
  - Processing during network interruptions or degraded connectivity
  - Behavior when patients are transferred between care units
  - Response to simultaneous alerts from multiple patients
  - Management of conflicting or physiologically improbable readings

- **Required Test Coverage Metrics**:
  - 100% coverage of device protocol implementation
  - >95% line coverage for all production code
  - 100% validation against annotated clinical datasets
  - Comprehensive testing across all supported medical devices
  - Full verification of compliance with regulatory requirements

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

1. Reliable integration with diverse medical device protocols
2. Accurate calibration of patient-specific baseline parameters
3. Effective assessment of signal quality with appropriate artifact rejection
4. Precise detection and classification of clinically significant events
5. Comprehensive logging with appropriate privacy controls
6. Scalability to support hospital-wide monitoring needs
7. Compliance with all relevant healthcare regulations
8. Comprehensive test coverage with all tests passing

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