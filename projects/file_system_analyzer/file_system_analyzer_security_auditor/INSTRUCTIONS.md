# Sensitive Data Discovery & Compliance System

## Overview
A specialized file system analysis library focused on identifying, tracking, and reporting sensitive information for regulatory compliance. This solution enables comprehensive security audits through pattern-based scanning, detailed logging, and compliance-ready reporting capabilities.

## Persona Description
Priya works as an information security specialist conducting regular audits for regulatory compliance. She needs to identify potentially sensitive files stored in unauthorized locations and verify that data retention policies are being properly enforced.

## Key Requirements
1. **Pattern-based scanning for sensitive information**
   - Implement sophisticated content analysis capabilities to detect PII and sensitive data based on predefined and customizable patterns
   - Support various data types including social security numbers, credit card information, health data, and other regulated information
   - Enable contextual analysis to reduce false positives while maintaining high detection rates
   - Provide detection confidence scores with justification for flagged content

2. **Comprehensive audit logging system**
   - Create immutable, tamper-evident logging for all scan operations
   - Capture detailed metadata including who initiated scans, what parameters were used, and what was discovered
   - Implement cryptographic verification for log integrity
   - Support for log rotation, archival, and secure retrieval for audit evidence

3. **Customizable compliance report templates**
   - Develop a flexible reporting framework with templates mapped to specific regulatory frameworks (GDPR, HIPAA, SOX, etc.)
   - Support for detailed evidence collection and organization by compliance requirement
   - Include metadata mapping between discovered items and specific regulatory clauses
   - Enable export in various formats suitable for submission to regulatory bodies

4. **Differential scanning capabilities**
   - Implement efficient comparison between current and previous scan results
   - Highlight newly added, modified, or removed sensitive content since previous audit
   - Track the migration of sensitive content between authorized and unauthorized locations
   - Provide trend analysis of compliance violations over time

5. **Chain-of-custody tracking**
   - Implement cryptographic verification for exported reports
   - Maintain tamper-evident record of all handling of discovered sensitive information
   - Create verifiable audit trail for all actions taken on discovered data
   - Support digital signatures and timestamps for legal defensibility

## Technical Requirements
- **Accuracy**: False positive rate must be under 5% with false negative rate under 1% for defined sensitive data patterns
- **Performance**: Scanning must be optimized to handle large file systems with minimal impact on operations
- **Security**: Implementation must follow security-by-design principles with all sensitive data handled according to appropriate standards
- **Auditability**: All operations must be fully auditable with tamper-evident logging
- **Compliance**: The system itself must meet relevant compliance requirements for security tools

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Pattern Detection Engine**
   - Regular expression and machine learning-based content analysis
   - Predefined pattern libraries for common sensitive data types
   - Content extraction from various file formats (PDF, Office documents, images via OCR, etc.)
   - Scoring mechanism for detection confidence

2. **Secure Audit Logging**
   - Cryptographically secured logging infrastructure
   - Detailed event recording with full provenance information
   - Immutable storage with tamper detection
   - Searchable and exportable logs with appropriate access controls

3. **Compliance Reporting System**
   - Template-based report generation mapped to specific regulations
   - Evidence collection and organization functions
   - Metadata enrichment for regulatory context
   - Export capabilities in various formats (PDF, HTML, JSON, etc.)

4. **Differential Analysis Engine**
   - Efficient storage of previous scan results
   - Change detection algorithms for content and location
   - Time-series analysis of compliance state
   - Anomaly detection in compliance patterns

5. **Chain of Custody Framework**
   - Cryptographic verification mechanisms
   - Digital signature and timestamp integration
   - Verifiable export functions with integrity checking
   - Complete action tracking for all discovered sensitive data

## Testing Requirements
- **Pattern Detection Testing**
  - Test against standardized datasets of various sensitive information types
  - Validate detection accuracy metrics (precision, recall, F1 score)
  - Benchmark performance with large and complex file collections
  - Test against obfuscated or partially masked sensitive data

- **Logging System Testing**
  - Verify tamper detection with deliberately modified logs
  - Test log integrity under various failure conditions
  - Validate completeness of captured metadata
  - Verify performance with high-volume logging scenarios

- **Compliance Reporting Testing**
  - Validate correct mapping of findings to regulatory requirements
  - Test report generation with various template configurations
  - Verify accuracy of evidence collection and presentation
  - Test with mock regulatory submission requirements

- **Differential Analysis Testing**
  - Test accuracy of change detection with known modifications
  - Validate performance with large historical datasets
  - Test boundary conditions for various change patterns
  - Verify trend analysis accuracy with synthetic data

- **Chain of Custody Testing**
  - Validate cryptographic verification under various scenarios
  - Test digital signature integration with various key configurations
  - Verify export integrity with deliberately tampered exports
  - Test audit trail completeness and accuracy

## Success Criteria
1. Successfully detect at least 99% of sensitive information across various file formats with false positive rate below 5%
2. Generate compliance reports that satisfy the documentation requirements for at least three major regulatory frameworks
3. Maintain cryptographically verifiable logs and chain of custody documentation that would be admissible as evidence
4. Accurately identify changes in sensitive data positioning with at least 99.5% accuracy
5. Process typical enterprise datasets (10+ million files) in under 8 hours with resource utilization below 20%
6. Pass independent security audit of the tool itself against common vulnerability standards

To set up your development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```