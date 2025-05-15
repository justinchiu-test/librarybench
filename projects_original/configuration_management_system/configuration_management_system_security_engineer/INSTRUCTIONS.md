# Security-Focused Configuration Management System

## Overview
A specialized configuration management system designed to ensure configurations adhere to security standards and regulatory requirements. The system provides robust compliance validation, sensitive value encryption, comprehensive audit trails, granular access controls, and integration with security scanners to proactively identify security vulnerabilities in configurations.

## Persona Description
Marcus works on a security team responsible for ensuring that all configurations across the organization adhere to regulatory and internal security standards. His primary goal is to audit configuration changes for security implications and enforce encryption of sensitive values.

## Key Requirements
1. **Compliance Rule Engine that Validates Configurations Against Security Policies** - Provides a powerful rule engine that evaluates configuration settings against a comprehensive set of security policies, identifying non-compliant configurations and policy violations. This is critical for Marcus because his organization must adhere to multiple regulatory frameworks (GDPR, HIPAA, SOC2, PCI-DSS), and manual verification of compliance across thousands of configuration values is impractical.

2. **Sensitive Value Encryption with Key Rotation Management** - Implements automatic encryption for sensitive configuration values (passwords, API keys, tokens) with sophisticated key management that supports regular key rotation without service disruption. This is essential because Marcus's organization has experienced breaches in the past due to unencrypted sensitive values in configuration files checked into version control.

3. **Configuration Change Audit Trails with Security Impact Annotations** - Maintains a detailed, tamper-proof audit trail of all configuration changes with annotations describing the potential security impact of each change, supporting forensic investigations and compliance reporting. This functionality allows Marcus to quickly investigate security incidents, provide evidence during audits, and track the introduction of security-relevant configuration changes.

4. **Attribute-based Access Control for Security-Sensitive Configuration Sections** - Enforces fine-grained, attribute-based access control rules that restrict which users can modify security-critical configuration sections based on their role, department, and security clearance level. This prevents unauthorized personnel from modifying security controls, addressing a key concern for Marcus as the company scales its engineering team globally.

5. **Security Scanning Integration that Tests Configurations Against Vulnerability Databases** - Integrates with security vulnerability databases and scanning tools to proactively identify security risks in configurations before they're deployed, such as use of deprecated encryption algorithms or known vulnerable software versions. This allows Marcus to shift security verification left in the development process, preventing vulnerable configurations from reaching production.

## Technical Requirements
- **Testability Requirements**: All security rules must be individually testable. Mock vulnerability databases must be provided for testing scanner integration. Encryption and key rotation functionality must be testable with deterministic keys for reproducible tests.

- **Performance Expectations**: Security rule validation must complete within 3 seconds even for complex configurations with thousands of properties. Encryption/decryption operations must add no more than 100ms overhead to configuration access.

- **Integration Points**:
  - Must integrate with external key management systems (HashiCorp Vault, AWS KMS, etc.)
  - Must support OVAL and STIX for vulnerability description
  - Must provide hooks for integration with SIEM systems
  - Must generate reports compatible with common compliance frameworks

- **Key Constraints**:
  - Must support air-gapped environments for high-security deployments
  - Must maintain FIPS 140-2 compliance for cryptographic operations
  - Must not expose sensitive values in logs or error messages
  - Must maintain backward compatibility for encrypted values during key rotation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality required for this security-focused configuration management system includes:

1. **Security Policy Rule Engine**:
   - DSL for expressing security compliance rules
   - Rule evaluation engine that processes configurations against rules
   - Rule versioning and lifecycle management
   - Compliance reporting with violation details

2. **Sensitive Value Protection**:
   - Transparent encryption/decryption of sensitive values
   - Support for multiple encryption algorithms
   - Key rotation mechanism with zero downtime
   - Key access auditing and security controls

3. **Audit and Change Tracking**:
   - Comprehensive, tamper-evident logging of all configuration operations
   - Security impact classification for configuration changes
   - Historical configuration state reconstruction
   - Compliance reporting for audit purposes

4. **Access Control System**:
   - Attribute-based access control model
   - Fine-grained permission rules for configuration sections
   - Integration with enterprise identity systems
   - Privilege escalation workflows for emergency access

5. **Security Vulnerability Scanning**:
   - Integration with vulnerability databases (CVE, NVD)
   - Configuration pattern matching against known vulnerabilities
   - Risk scoring for identified issues
   - Remediation guidance generation

6. **Security Metadata Management**:
   - Tagging system for security-relevant configuration items
   - Classification of configuration data sensitivity
   - Dependency tracking for security impact analysis
   - Expiration and review date tracking for credentials

## Testing Requirements
The implementation must include comprehensive pytest tests that validate all aspects of the system:

- **Key Functionalities to Verify**:
  - Accurate evaluation of security compliance rules
  - Proper encryption and decryption of sensitive values
  - Complete and accurate audit trails of configuration changes
  - Correct enforcement of access control policies
  - Accurate identification of security vulnerabilities in configurations

- **Critical User Scenarios**:
  - Adding new security compliance rules
  - Rotating encryption keys without service disruption
  - Investigating configuration changes during a security incident
  - Managing access permissions for security-sensitive configurations
  - Scanning configurations for newly discovered vulnerabilities

- **Performance Benchmarks**:
  - Security rule validation must complete within 3 seconds for 10,000 configuration items
  - Encryption operations must process 1,000 sensitive values per second
  - Audit logging must handle 500 operations per second
  - Access control decisions must be made within 50ms
  - Vulnerability scanning must process configurations at a rate of 5MB per second

- **Edge Cases and Error Conditions**:
  - Handling conflicting security rules
  - Recovering from key management service outages
  - Detecting tampering with audit logs
  - Managing access control during identity system outages
  - Handling malformed vulnerability database entries

- **Required Test Coverage Metrics**:
  - Minimum 95% line coverage for security-critical modules
  - 100% coverage of encryption/decryption code paths
  - All security rules must have both positive and negative test cases
  - All error handling paths must be tested
  - All access control scenarios must be verified

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
The implementation will be considered successful when:

1. All security compliance rules are correctly evaluated against configurations.
2. Sensitive values are properly encrypted, with support for key rotation.
3. Comprehensive audit trails are maintained for all configuration changes.
4. Access control correctly limits modification of security-sensitive configurations.
5. Security vulnerability scanning correctly identifies potential issues.
6. All specified performance benchmarks are met consistently.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
To set up the development environment:

1. Navigate to the project directory
2. Create a virtual environment using `uv venv`
3. Activate the environment with `source .venv/bin/activate`
4. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

The pytest_results.json file must be submitted as evidence that all tests pass successfully.