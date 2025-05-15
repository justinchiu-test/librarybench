# Financial Regulatory DSL Toolkit

## Overview
A specialized Domain Specific Language toolkit designed for financial institutions to create, validate, and implement regulatory compliance rules. This toolkit enables compliance officers and financial analysts to express complex regulatory constraints in a natural language-like syntax while ensuring these rules are correctly translated into trading system validations without requiring deep programming knowledge.

## Persona Description
Sophia works at a large investment bank where complex regulatory compliance rules need to be encoded into trading systems. Her primary goal is to create a domain-specific language that allows compliance officers to express regulatory constraints in a natural way while ensuring these rules are correctly translated into trading system validations.

## Key Requirements
1. **Financial regulation template library with jurisdiction-specific rule patterns**: A comprehensive collection of templates for common regulatory requirements across different jurisdictions (US SEC, EU MiFID, etc.) that can be customized and combined. This is critical because it allows compliance officers to quickly implement new regulations without creating rules from scratch and ensures consistency across similar regulatory requirements.

2. **Rule contradiction and conflict detection with resolution suggestions**: An analysis engine that can identify when two or more rules contradict or overlap, with intelligent suggestions for resolution. This is essential because financial institutions must navigate complex and sometimes conflicting regulations across multiple jurisdictions, and undetected conflicts could lead to compliance failures.

3. **Natural language approximation for financial compliance terminology**: A syntax that closely resembles natural language specific to financial compliance, allowing non-technical compliance officers to read, verify, and author rules. This is vital because it reduces the translation errors between regulatory text and implementation and empowers domain experts to directly participate in rule creation.

4. **Auditability through rule provenance and version tracking**: Built-in capabilities to track the origin, justification, and evolution of each rule, including which regulation inspired it and how it has changed over time. This is crucial for demonstrating compliance to regulators, understanding the reasoning behind historical decisions, and maintaining an audit trail for governance purposes.

5. **Integration with financial transaction systems via standardized interfaces**: Predefined interfaces to connect with trading platforms, risk management systems, and transaction processing pipelines. This is necessary because rules must be applied to actual financial operations in real-time to prevent non-compliant transactions and generate required reports.

## Technical Requirements
- **Testability Requirements**:
  - Unit tests must verify each template against known regulatory examples
  - Integration tests must validate rule application on sample transaction datasets
  - Conflict detection algorithms must be verified against known conflicting rule sets
  - Performance tests must confirm rule evaluation speed meets trading system requirements
  - All components must achieve at least 90% test coverage

- **Performance Expectations**:
  - Rule validation must complete in under 50ms per transaction for high-frequency trading compatibility
  - Conflict detection for a ruleset of 1000+ rules must complete in under 60 seconds
  - System must scale to handle 10,000+ unique rules without significant performance degradation
  - Memory footprint must remain under 1GB for full ruleset operation

- **Integration Points**:
  - Standardized interfaces for connecting to trading platforms (FIX protocol)
  - API for regulatory reporting systems
  - Import/export functionality for common compliance formats (XML, JSON)
  - Integration with regulatory update feeds to flag potentially affected rules

- **Key Constraints**:
  - Implementation must be in Python with no UI components
  - All rule logic must be expressible through the DSL without requiring custom code
  - Rule definitions must be storable as human-readable text files
  - System must not require modification to process new regulation types

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Financial Regulatory DSL Toolkit must provide:

1. A domain-specific language parser and interpreter specialized for financial regulations
2. A template system for creating and customizing regulatory rule patterns
3. A rule validation engine that can apply rules to financial transaction data
4. Conflict detection algorithms that identify contradictions between rules
5. A rule management system for version control and provenance tracking
6. Standardized interfaces for integration with financial systems
7. A natural language processing component to translate between regulatory text and DSL syntax
8. Export mechanisms for deploying rules to production environments
9. Documentation generators that produce human-readable explanations of implemented rules
10. Test utilities for verifying rule correctness against sample data

The system should enable compliance officers to define rules such as:
- Trading limits and thresholds
- Prohibited transaction types
- Required approvals and validations
- Reporting triggers
- Cross-border transaction requirements
- Client classification rules
- Disclosure requirements

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct parsing of DSL syntax into executable rule representations
  - Accurate detection of rule conflicts and contradictions
  - Proper application of rules to transaction data
  - Correct version tracking and provenance information
  - Successful integration with external systems through defined interfaces

- **Critical User Scenarios**:
  - Compliance officer creates new rule from regulatory text
  - Analyst identifies and resolves conflicts between multi-jurisdictional rules
  - Audit team retrieves provenance information for compliance verification
  - Risk team updates existing rules to accommodate regulatory changes
  - System applies complex rule combinations to high-volume transaction streams

- **Performance Benchmarks**:
  - Parse and compile 100 rules in under 10 seconds
  - Validate 10,000 transactions against 500 rules in under 5 minutes
  - Detect conflicts in a ruleset of 1000 rules in under 60 seconds
  - Memory usage must not exceed 1GB during normal operation

- **Edge Cases and Error Conditions**:
  - Handling of circular rule references
  - Graceful degradation when transaction volume exceeds capacity
  - Recovery from invalid rule definitions
  - Detection of subtly contradictory rules (not just direct conflicts)
  - Behavior when integration endpoints are unavailable

- **Required Test Coverage Metrics**:
  - Minimum 90% code coverage across all modules
  - 100% coverage of rule parser and interpreter
  - 100% coverage of conflict detection algorithms
  - 95% coverage of system integration components

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

1. All five key requirements are fully implemented and operational
2. Each requirement passes its associated test scenarios
3. The system demonstrates the ability to express real-world financial regulations in the DSL
4. Rule conflicts are correctly identified with appropriate resolution suggestions
5. Performance benchmarks are met for rule processing and transaction validation
6. Integration with standard financial interfaces is demonstrated
7. The natural language approximation makes rules readable by non-technical compliance staff
8. Full auditability is maintained through comprehensive provenance tracking

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
To set up the development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```