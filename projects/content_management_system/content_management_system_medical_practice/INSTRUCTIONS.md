# Healthcare Practice CMS

A specialized content management system designed for medical practices to communicate services, provider information, and health resources while maintaining compliance and accessibility standards.

## Overview

Healthcare Practice CMS is a comprehensive content management library tailored for medical practices. It enables practice managers to maintain accurate provider information, communicate office policies, ensure healthcare compliance standards, meet accessibility requirements, and provide multilingual content for diverse patient populations, all while focusing on patient needs and medical accuracy.

## Persona Description

David manages a family medical practice website that needs to communicate services, provider information, and health resources to patients. His primary goal is to maintain accurate provider information and office policies while ensuring all content meets healthcare compliance standards and accessibility requirements.

## Key Requirements

1. **Provider Directory with Credential Verification**: Develop a comprehensive provider management system that displays and verifies medical credentials and specialties. This is critical for David as it builds patient trust by confirming doctors' qualifications, helps patients select appropriate specialists, and satisfies regulatory requirements for transparency in provider credentials and board certifications.

2. **HIPAA-Compliant Form System**: Create a secure form creation and management system that handles patient information requests while maintaining strict HIPAA compliance. This feature is essential as it allows patients to safely communicate with the practice about sensitive health matters, request appointments or prescription refills, while ensuring all data collection and storage meets federally-mandated patient privacy requirements.

3. **Accessibility Compliance Framework**: Implement a content validation system that ensures all published content meets Web Content Accessibility Guidelines (WCAG) standards. This functionality is vital for making the practice's digital resources accessible to patients with disabilities (visual, hearing, motor, cognitive), avoiding potential legal issues, and demonstrating the practice's commitment to serving all patients equally.

4. **Multilingual Content Management**: Develop a robust translation and localization system for managing content in multiple languages. This capability is crucial for effectively communicating with non-English speaking patients in a diverse community, ensuring they understand medical instructions and services, and providing equitable healthcare access to all patient populations the practice serves.

5. **Structured Health Information Templates**: Create specialized content templates for medical information with citation support for authoritative sources. This feature is important for presenting consistent, accurate health information to patients, maintaining the practice's credibility through evidence-based content, and efficiently organizing complex medical topics in patient-friendly formats.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 95% coverage
- HIPAA compliance features must be thoroughly tested
- Accessibility validation must be verifiable through automated and manual test cases
- Multilingual content handling must be validated with test fixtures
- Content templates must be tested for proper rendering

### Performance Expectations
- Provider directory searches must complete within 100ms
- Form submissions must be securely processed within 500ms
- Accessibility checking should complete within 1s per page
- Language switching should occur within 200ms
- Content rendering must be optimized for varying connection speeds

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Electronic Health Record (EHR) system APIs
- Prescription management system integration
- Medical terminology and coding databases
- Insurance verification services

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Must fully comply with healthcare regulations

## Core Functionality

The library must provide the following core components:

1. **Provider Management System**:
   - Provider profiles with credentials and specialties
   - Verification status tracking
   - Scheduling and availability information
   - Specialty and insurance acceptance filtering
   - Provider search optimization

2. **Secure Forms Framework**:
   - HIPAA-compliant form builder
   - Secure data collection and storage
   - Encrypted transmission
   - Audit logging and access controls
   - Data retention and purging policies

3. **Accessibility Compliance**:
   - WCAG validation and enforcement
   - Alternative text management
   - Document structure verification
   - Color contrast analysis
   - Screen reader compatibility

4. **Translation and Localization**:
   - Language variant management
   - Translation workflow and versioning
   - Language-specific content adaptation
   - Character encoding handling
   - Right-to-left language support

5. **Health Content System**:
   - Medical content templates
   - Evidence citation and verification
   - Medical terminology management
   - Condition and treatment information
   - Medication and procedure descriptions

6. **Policy and Compliance**:
   - Office policy management
   - Terms of service and privacy policies
   - Compliance document versioning
   - Required disclosures management
   - Patient information security

## Testing Requirements

### Key Functionalities to Verify
- Creation, updating, and verification of provider credentials
- Secure processing of patient information through forms
- Accurate validation of content against accessibility standards
- Proper handling and display of multilingual content
- Correct formatting and citation of health information

### Critical User Scenarios
- Patients finding and evaluating providers by specialty and credentials
- Submitting protected health information through secure forms
- Accessing content with assistive technologies
- Switching language preferences and receiving properly translated content
- Researching specific health conditions with cited medical information

### Performance Benchmarks
- Directory search response time with varying filter criteria
- Form processing time with different types of patient data
- Accessibility validation time for complex content
- Language switching speed with different content volumes
- Health information template rendering with various medical topics

### Edge Cases and Error Conditions
- Handling incomplete or pending provider credentials
- Managing form submissions with sensitive data when storage issues occur
- Recovering from accessibility validation failures
- Behavior when translated content is missing or incomplete
- Managing citations for medical information when sources change

### Required Test Coverage Metrics
- Minimum 95% line coverage for all core components
- 100% coverage of HIPAA-related code
- All error handling paths must be tested
- Performance tests for search and form submission
- Accessibility compliance validation tests

## Success Criteria

The implementation will be considered successful when:

1. Patients can find accurate, verified information about all practice providers
2. Protected health information can be securely submitted and processed
3. All content meets or exceeds WCAG accessibility standards
4. Non-English speaking patients can access all critical information in their preferred language
5. Health information is presented in structured, evidence-based formats with proper citations
6. All operations can be performed programmatically through a well-documented API
7. The entire system can be thoroughly tested using pytest with high coverage
8. Performance meets or exceeds the specified benchmarks
9. All functionality is fully compliant with healthcare regulations

## Setup and Development

To set up your development environment:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install necessary development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest path/to/test.py::test_function_name
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

Remember to adhere to the code style guidelines in the project's CLAUDE.md file, including proper type hints, docstrings, and error handling.