# Business Process Modeling Language

A domain-specific language toolkit for defining, analyzing, and optimizing organizational workflows.

## Overview

This project delivers a specialized domain-specific language toolkit that bridges the gap between business process diagrams and executable workflow code. The toolkit enables business analysts to define precise process workflows, role-based access patterns, performance indicators, and compliance rules without requiring programming expertise, while generating code that can be directly executed by workflow engines and business process management systems.

## Persona Description

Priya helps organizations optimize their operational workflows and business processes. Her primary goal is to develop a business process language that bridges the gap between process diagrams created by business analysts and executable workflow code implemented by IT teams.

## Key Requirements

1. **BPMN (Business Process Model and Notation) compliant visual editor**
   - Essential for Priya because business analysts typically express processes using BPMN diagrams, and a seamless translation between these visual models and executable code is required to maintain accuracy and reduce implementation errors.
   - The DSL must support bidirectional transformation between BPMN diagram representations and executable process code, ensuring that process definitions can be visualized and modified using standard BPMN notation.

2. **Role-based access patterns for organizational processes**
   - Critical because business processes span multiple roles and departments with different responsibilities and permissions, and Priya needs to ensure that process implementations correctly enforce organizational boundaries and access controls.
   - The system must provide syntax for defining role-based responsibilities, permissions, and handoffs within process flows, validating that all activities have appropriate role assignments.

3. **KPI (Key Performance Indicator) definition and monitoring integration**
   - Vital because process improvements require measurable outcomes, and Priya needs to define performance metrics directly within process definitions to enable ongoing measurement and optimization.
   - The DSL must support defining KPI collection points, calculation methods, and target thresholds within process flows, with integration hooks for external analytics and monitoring systems.

4. **Resource allocation optimization with constraint solving**
   - Necessary because efficient business processes must appropriately balance resource utilization across activities and departments, and Priya needs to define resource constraints and optimization goals.
   - The toolkit must provide mechanisms for specifying resource requirements, constraints, and allocation policies, with algorithms to validate feasibility and optimize resource distribution.

5. **Compliance rule checking for industry-specific regulations**
   - Important because many business processes must adhere to regulatory requirements specific to their industry, and Priya needs to ensure that processes implement required compliance measures.
   - The system must support defining compliance checkpoints, validation rules, and regulatory requirements within process definitions, with automated verification against applicable standards.

## Technical Requirements

- **Testability Requirements**
  - All process definitions must be testable with simulated workflow executions
  - Role-based access controls must be verifiable through scenario testing
  - KPI calculations must produce consistent, validated results
  - Resource allocation algorithms must be testable with simulated resource pools
  - Compliance rule enforcement must be verifiable through audit scenarios

- **Performance Expectations**
  - Process validation must complete within 5 seconds for typical business processes
  - Resource optimization calculations must complete within 10 seconds
  - The system must handle process definitions with up to 300 activities
  - Memory usage must not exceed 250MB for the toolkit core
  - The system must support concurrent analysis of up to 50 process definitions

- **Integration Points**
  - Business Process Management (BPM) systems for workflow execution
  - Enterprise Resource Planning (ERP) systems for resource data
  - Business Intelligence (BI) platforms for KPI monitoring
  - Identity and Access Management (IAM) systems for role validation
  - Governance, Risk, and Compliance (GRC) systems for regulatory verification

- **Key Constraints**
  - Must support incremental process implementation and deployment
  - Must handle long-running processes with persistence requirements
  - Must accommodate dynamic process modifications at runtime
  - Must provide detailed process execution logs for audit purposes
  - Must operate within enterprise security frameworks and policies

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. The BPMN representation should generate structured data that could be visualized by external tools, not implementing the visualization itself.

## Core Functionality

The core functionality of the Business Process Modeling Language encompasses:

1. **Process Definition Language**
   - Business domain-specific syntax for workflow activities and transitions
   - BPMN-compliant constructs for gateways, events, and activities
   - Exception handling and compensation mechanisms
   - Subprocess encapsulation and reuse
   - Process versioning and variant management

2. **Role and Access Control System**
   - Organizational role definition and hierarchy
   - Permission specification for process activities
   - Handoff and approval workflow patterns
   - Delegation and escalation rule definition
   - Separation of duties enforcement

3. **Performance Measurement Framework**
   - KPI definition with calculation methods
   - Process instrumentation points for data collection
   - Target threshold specification
   - Trending and variance analysis
   - Performance dashboard data generation

4. **Resource Management Engine**
   - Resource type and capability modeling
   - Allocation policy definition
   - Constraint specification for availability and capacity
   - Optimization goal definition (cost, time, quality)
   - Resource utilization analysis and forecasting

5. **Compliance Verification System**
   - Regulatory requirement specification
   - Compliance validation rule definition
   - Mandatory control point identification
   - Audit trail generation for verification
   - Gap analysis for compliance coverage

## Testing Requirements

- **Key Functionalities to Verify**
  - Process definition parsing and validation against BPMN standards
  - Role-based access control enforcement throughout process execution
  - KPI calculation accuracy under various process scenarios
  - Resource optimization effectiveness with constrained resources
  - Compliance rule verification across industry-specific regulations

- **Critical User Scenarios**
  - Business analyst defining a process that spans multiple departments
  - Testing process behavior with different user roles and permissions
  - Measuring process performance against defined KPIs
  - Optimizing resource allocation for efficiency and throughput
  - Validating process compliance with relevant regulations

- **Performance Benchmarks**
  - Process validation: < 5 seconds for 100-activity processes
  - BPMN transformation: < 3 seconds for bidirectional conversion
  - KPI calculation: < 2 seconds for performance metric generation
  - Resource optimization: < 10 seconds for allocation solving
  - Compliance checking: < 5 seconds for full regulatory validation

- **Edge Cases and Error Conditions**
  - Handling incomplete or inconsistent process definitions
  - Managing circular process references and infinite loops
  - Addressing resource conflicts and allocation deadlocks
  - Graceful degradation when integrated systems are unavailable
  - Handling exceptional process paths and error recovery

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage for all modules
  - 100% coverage of process validation logic
  - Complete path coverage for all process execution flows
  - All resource allocation algorithms must be tested
  - Full coverage of compliance verification rules

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Business analysts can define executable workflows without IT department intervention
2. BPMN diagrams can be transformed to executable code and back with 95% fidelity
3. Role-based access controls are correctly enforced throughout process execution
4. KPI monitoring points correctly capture and calculate defined metrics
5. Resource allocation algorithms optimize resource usage within defined constraints
6. The system correctly validates processes against applicable compliance regulations
7. The test suite validates all core functionality with at least 90% coverage
8. Performance benchmarks are met under typical business process loads

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
uv run pytest tests/test_process_validator.py::test_bpmn_compliance

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into business process management systems rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs, with a clear separation between the process definition language and any future visualization or UI components.