# StoryTracker - A Knowledge Management System for Investigative Journalists

## Overview
StoryTracker is a specialized knowledge management system designed for investigative journalists who need to connect sources, documents, and interviews while tracking the evolution of developing stories. It provides tools for managing information provenance, assessing evidence strength, tracking investigations chronologically, organizing material for different story angles, and protecting sensitive sources.

## Persona Description
Chen investigates complex stories involving government policy, corporate behavior, and public impact. He needs to connect sources, documents, and interviews while tracking the evolution of developing narratives.

## Key Requirements
1. **Source relationship mapping** - Develop a comprehensive system for tracking information provenance and source credibility across complex investigations. This is critical for Chen to maintain journalistic integrity by documenting where each piece of information originated, establishing the reliability hierarchy of different sources, and tracking how sources connect to one another. The system must support anonymous source protection while maintaining verifiable information chains.

2. **Evidence strength assessment** - Create a framework for linking claims to supporting documentation and evaluating the quality of evidence. This capability is essential for Chen to evaluate the robustness of different story elements, identify areas requiring additional corroboration, and prioritize the most substantiated aspects of an investigation. The system should support multiple evidence types (documents, testimonials, data) with appropriate strength criteria for each.

3. **Chronological investigation tracking** - Implement a timeline system revealing how information emerged over time during an investigation. This feature allows Chen to document the progressive discovery of facts, identify potential patterns in information disclosure, recognize when information changes over time, and maintain a clear record of the investigative process for editorial review and potential legal scrutiny.

4. **Narrative development workspaces** - Design specialized workspaces for organizing material around different story angles or narrative approaches. This capability helps Chen explore multiple interpretations of complex stories, develop alternative narrative structures based on the same evidence base, and efficiently organize large volumes of information according to different journalistic frameworks (exposé, profile, explanatory, etc.).

5. **Secure source protection** - Implement robust mechanisms for compartmentalizing sensitive information and protecting confidential sources. This feature is vital for Chen to fulfill ethical obligations to vulnerable sources, maintain information security when working on politically sensitive stories, and separate identifying details from usable information. The system must support encryption, anonymization, and access controls for different information sensitivity levels.

## Technical Requirements
- **Testability Requirements**:
  - All modules must have comprehensive unit tests with at least 90% code coverage
  - Source mapping functionality must be testable with simulated source networks
  - Evidence assessment algorithms must be verifiable against predefined evaluation criteria
  - Timeline functionality must be tested with complex, non-linear information emergence scenarios
  - Security features must undergo rigorous testing for information isolation and access control

- **Performance Expectations**:
  - System must handle investigations with 500+ sources and 10,000+ documents
  - Source graph operations must complete in under 1 second for typical source networks
  - Evidence strength calculations must process 1,000+ evidence items in under 3 seconds
  - Full-text search across the evidence repository must return results in under 2 seconds
  - Security operations (encryption/decryption) must not significantly impact system performance

- **Integration Points**:
  - Support for importing documents from common formats (PDF, DOCX, TXT, etc.)
  - Integration capabilities for public records databases and FOIA request tracking
  - Export functionality for source maps and timelines in portable formats
  - Secure backup mechanisms for sensitive investigation materials
  - Support for structured data extraction from tabular sources (CSV, Excel)

- **Key Constraints**:
  - All data must be stored locally to avoid cloud security vulnerabilities
  - Implementation must support compartmentalized security with different access levels
  - No user interface components - all functionality exposed through APIs only
  - Core functionality must work offline for field reporting conditions
  - Code base must be auditable for security verification

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
StoryTracker needs to implement these core capabilities:

1. **Source Management System**: A comprehensive framework for handling information sources with:
   - Source entity representation with credibility metrics and relationship attributes
   - Hierarchical source classification (primary, secondary, anonymous, etc.)
   - Attribution tracking linking information to specific sources
   - Source network visualization capabilities using text/ASCII representations
   - Anonymization protocols for sensitive sources

2. **Evidence Repository**: A secure system for managing investigative materials:
   - Document storage with metadata retention and content indexing
   - Evidence classification framework by type and relevance
   - Strength assessment algorithms for different evidence categories
   - Claim-to-evidence linking with support for multiple evidence items per claim
   - Contradiction and corroboration detection between evidence items

3. **Investigation Timeline**: A temporal tracking system with:
   - Multi-resolution time tracking (days to years) for long-running investigations
   - Information emergence recording with timestamp precision
   - Parallel timeline support for multiple related narrative threads
   - Key event flagging and milestone tracking
   - Timeline comparison tools for identifying temporal patterns

4. **Narrative Workspace**: A framework for story development:
   - Story angle definition with thematic tagging
   - Material organization by narrative relevance and role
   - Draft progression tracking through multiple versions
   - Evidence strength visualization within narrative contexts
   - Gap analysis for identifying underdeveloped story elements

5. **Security Framework**: A robust system for information protection:
   - Encryption for sensitive materials with key management
   - Access control for different information sensitivity levels
   - Anonymization tools for source protection
   - Secure deletion capabilities for sensitive materials
   - Audit logging for evidence handling compliance

## Testing Requirements
The implementation must include comprehensive tests that verify all aspects of the system:

- **Key Functionalities to Verify**:
  - Source relationship mapping correctly tracks information provenance and credibility
  - Evidence strength assessment accurately evaluates documentation quality across different evidence types
  - Chronological tracking captures information emergence patterns accurately
  - Narrative workspaces effectively organize material for different story angles
  - Security mechanisms properly protect sensitive sources and information

- **Critical User Scenarios**:
  - Adding new sources and establishing their relationships to existing sources
  - Assessing the strength of newly acquired evidence and its impact on story credibility
  - Tracking how a key piece of information evolved through an investigation
  - Organizing the same evidence base for multiple potential story angles
  - Securing sensitive source information while maintaining usable attribution

- **Performance Benchmarks**:
  - Source graph operations must handle networks with 1,000+ nodes efficiently
  - Evidence strength algorithms must evaluate 5,000+ documents in under 10 seconds
  - Timeline operations must support 10,000+ events without performance degradation
  - Narrative workspace switching must occur in under 1 second regardless of content volume
  - Encryption/decryption operations must process at least 10MB/second

- **Edge Cases and Error Conditions**:
  - Handling circular source references or attribution loops
  - Managing conflicting evidence with contradictory content
  - Dealing with retrospective timeline revisions as new information emerges
  - Recovering from security key loss scenarios
  - Managing extremely large document repositories (100,000+ items)

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for security-critical components
  - 95% branch coverage for evidence assessment algorithms
  - 95% coverage for source relationship management
  - 100% coverage for sensitive data handling functions

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
The implementation will be considered successful if it meets the following criteria:

1. Journalists can map complex source relationships while maintaining source credibility metrics
2. Evidence can be assessed for strength with clear links between claims and supporting documentation
3. Information emergence can be tracked chronologically throughout an investigation
4. Content can be organized into different narrative workspaces for story development
5. Sensitive sources and information can be securely protected with appropriate access controls

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment:
1. Use `uv venv` to create a virtual environment
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL REMINDER: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```