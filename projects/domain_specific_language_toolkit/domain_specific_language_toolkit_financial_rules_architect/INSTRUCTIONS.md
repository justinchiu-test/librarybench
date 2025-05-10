# Financial Regulatory DSL Toolkit

A domain-specific language framework tailored for financial compliance rule definition and enforcement.

## Overview

This project provides a specialized domain-specific language toolkit that enables financial compliance officers to express complex regulatory constraints in a natural, domain-appropriate way. The toolkit translates these human-readable rule definitions into enforceable validation logic that integrates with trading and financial transaction systems, ensuring regulatory compliance while providing auditability and traceability.

## Persona Description

Sophia works at a large investment bank where complex regulatory compliance rules need to be encoded into trading systems. Her primary goal is to create a domain-specific language that allows compliance officers to express regulatory constraints in a natural way while ensuring these rules are correctly translated into trading system validations.

## Key Requirements

1. **Financial regulation template library with jurisdiction-specific rule patterns**
   - Essential for Sophia as it allows compliance officers to quickly adapt to varying regulatory frameworks across different markets without requiring deep technical knowledge of each jurisdiction's specific implementation details.
   - The system must provide pre-defined templates for common regulatory frameworks (e.g., MiFID II, Dodd-Frank, Basel III) that can be extended or customized.

2. **Rule contradiction and conflict detection with resolution suggestions**
   - Critical because financial regulations from different jurisdictions or regulatory bodies can create conflicting requirements, and Sophia needs to ensure the bank's systems enforce the most stringent applicable rule while documenting exceptions.
   - The toolkit must analyze rule definitions to identify logical contradictions or conflicts, providing detailed reporting and suggesting possible resolution strategies.

3. **Natural language approximation for financial compliance terminology**
   - Vital because compliance officers typically express rules using domain-specific financial and legal terminology, and Sophia needs to minimize the translation gap between their natural expression and formal rule definition.
   - The DSL must closely match the vocabulary and constructs used in regulatory documents and compliance team communications.

4. **Auditability through rule provenance and version tracking**
   - Essential for regulatory examinations where Sophia's bank must demonstrate which rules were in effect at any given time, who approved them, and what regulatory requirements they implement.
   - All rules must maintain complete lineage information including source regulation, interpretation documentation, approval chain, and version history.

5. **Integration with financial transaction systems via standardized interfaces**
   - Necessary because rules defined in the DSL must be enforced at runtime in various trading systems, risk management platforms, and transaction processing systems throughout the bank.
   - The toolkit must generate integration code for multiple target platforms used in financial services while maintaining consistent rule enforcement.

## Technical Requirements

- **Testability Requirements**
  - Each rule must be independently testable with sample transaction data
  - Rule test cases must verify both positive compliance and violation detection
  - Testing framework must support mock transaction data generation
  - Tests must validate rule behavior across different jurisdictions and market conditions
  - Performance testing must verify rule evaluation speed for high-frequency trading scenarios

- **Performance Expectations**
  - Rule evaluation latency must be under 5ms for simple rules
  - Complex rule-sets must evaluate within 50ms to support trading workflows
  - The system must handle at least 10,000 rule evaluations per second
  - Memory usage must not exceed 500MB for the full ruleset

- **Integration Points**
  - Standard APIs for transaction validation workflows
  - Database connectors for rule persistence and audit logging
  - Event system for rule violation notifications
  - Export modules for regulatory reporting systems
  - Import capabilities for regulatory update feeds

- **Key Constraints**
  - Must work in air-gapped environments with no external dependencies
  - Must support both synchronous (pre-trade) and asynchronous (post-trade) validation
  - All rule changes must preserve audit history indefinitely
  - Must operate within existing compliance workflows and approval processes
  - All rule definitions must be exportable to human-readable formats for regulatory review

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality of the Financial Regulatory DSL Toolkit encompasses:

1. **Rule Definition Language**
   - A parser that processes domain-specific financial compliance rule syntax
   - Grammar definitions that closely mirror regulatory language
   - Type system for financial instruments, transaction properties, and market conditions
   - Semantic validation ensuring rules are logically consistent

2. **Rule Management System**
   - Version control with immutable rule history
   - Rule categorization by regulation, jurisdiction, and affected instruments
   - Rule relationship tracking for related or dependent rules
   - Rule activation/deactivation based on effective dates or emergency conditions

3. **Rule Transformation Engine**
   - Translation of DSL rules into executable validation logic
   - Optimization for performance in high-frequency trading environments
   - Generation of validation code for multiple target systems
   - Metadata preservation ensuring traceability from source rule to implementation

4. **Validation Framework**
   - Runtime rule evaluation against financial transactions
   - Transaction validation workflows defining when and how rules apply
   - Violation detection with detailed contextual information
   - Exception management with proper approval and documentation

5. **Audit and Compliance System**
   - Comprehensive logging of rule definitions, changes, and applications
   - Evidence gathering for regulatory examinations
   - Reporting on rule coverage, violations, and exceptions
   - Analytics on rule performance and effectiveness

## Testing Requirements

- **Key Functionalities to Verify**
  - Rule parsing and validation for all regulatory templates
  - Conflict detection between rules from different regulatory frameworks
  - Rule translation to executable validation logic
  - Transaction validation against defined rules
  - Complete audit trail creation and retrieval

- **Critical User Scenarios**
  - Compliance officer defining new rules based on regulatory changes
  - System detecting potential rule conflicts during definition
  - Transaction processing with real-time rule validation
  - Audit preparation with historical rule effectiveness reporting
  - Cross-jurisdictional rule application for global transactions

- **Performance Benchmarks**
  - Rule parsing: at least 100 new rules per second
  - Rule validation: less than 10ms per transaction for up to 100 applicable rules
  - Historical query: retrieval of rule audit trails within 500ms
  - Rule conflict detection: analysis of 1000 rule interactions in under 5 seconds
  - System initialization: loading full ruleset in under 30 seconds

- **Edge Cases and Error Conditions**
  - Handling of incomplete or ambiguous rule definitions
  - Management of circular dependencies between rules
  - Graceful degradation under extreme transaction volumes
  - Recovery from persistence failures without data loss
  - Proper handling of rules with retrospective effective dates

- **Required Test Coverage Metrics**
  - Minimum 95% code coverage for all core modules
  - 100% coverage of rule parsing and validation logic
  - Complete coverage of all regulatory templates
  - Full path coverage for rule application workflows
  - All error handling and exception paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Compliance officers can define regulatory rules using financial domain terminology without requiring developer assistance
2. The system can detect and highlight potential rule conflicts or contradictions with 95% accuracy
3. All defined rules maintain complete audit trails and version history, satisfying regulatory examination requirements
4. Rule validation integrates with existing transaction systems with latency impact of less than 10%
5. The system correctly enforces rules across jurisdictional boundaries for global transactions
6. Rule definitions can be traced directly to their regulatory sources with full provenance
7. The test suite validates all core functionality with at least 95% coverage
8. Performance benchmarks are met under expected production transaction volumes

## Getting Started

To set up the development environment:

```bash
# Initialize the project
uv init --lib

# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run a specific test
uv run pytest tests/test_rule_parser.py::test_regulatory_template_parsing

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into larger systems rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs.