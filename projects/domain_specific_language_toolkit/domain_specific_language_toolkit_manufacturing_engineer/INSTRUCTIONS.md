# Manufacturing Process Language Toolkit

A domain-specific language framework for defining, simulating, and executing complex manufacturing processes.

## Overview

This project delivers a specialized domain-specific language toolkit that enables manufacturing process engineers to define precise assembly workflows, equipment operations, and quality control checks without requiring programming expertise. The toolkit translates these process definitions into executable instructions for manufacturing systems while providing simulation capabilities to validate processes before deployment on the factory floor.

## Persona Description

Marcus designs automated manufacturing processes for an automotive company with complex assembly lines and quality control. His primary goal is to develop a language that allows process engineers to define manufacturing workflows and quality checks without requiring deep programming knowledge.

## Key Requirements

1. **Visual process flow designer that generates executable DSL code**
   - Critical for Marcus because most manufacturing engineers think visually about assembly processes, and a graphical representation allows them to see and validate the workflow while the system generates the corresponding executable code.
   - The toolkit must enable a programmatic way to represent visual process flows as code and vice versa, allowing the DSL to be the source of truth while supporting visual representations.

2. **Equipment-specific control syntax with vendor library integration**
   - Essential because automotive manufacturing involves diverse equipment from multiple vendors (robots, CNC machines, conveyor systems, etc.), each with their own control interfaces and protocols.
   - The DSL must provide abstractions that normalize control across different equipment while preserving equipment-specific capabilities and optimizations.

3. **Simulation environment for testing process definitions**
   - Vital for Marcus as testing manufacturing processes directly on production equipment is costly and potentially dangerous. Simulation allows process verification before physical deployment.
   - The system must accurately model timing, resource utilization, and physical interactions to predict potential issues in the real manufacturing environment.

4. **Fault handling pattern library for common manufacturing exceptions**
   - Necessary because manufacturing environments frequently encounter predictable failure modes (material jams, tool wear, calibration drift, supply interruptions), and Marcus needs standardized ways to detect and respond to these conditions.
   - The DSL must provide declarative fault detection patterns and recovery strategies that can be customized to specific equipment and processes.

5. **Physical constraint validation ensuring processes respect equipment limitations**
   - Critical because automated manufacturing equipment has well-defined operational limits (speed, load capacity, temperature ranges, cycle times), and processes must remain within these parameters to prevent damage and ensure quality.
   - The toolkit must validate that defined processes won't violate physical constraints of the specific equipment being used before execution.

## Technical Requirements

- **Testability Requirements**
  - All process definitions must be testable through simulation
  - Equipment interfaces must support mocking for isolated testing
  - Test fixtures for common manufacturing scenarios must be provided
  - Process assertions must verify timing, resource usage, and fault handling
  - Tests must validate constraint compliance for all equipment types

- **Performance Expectations**
  - Process compilation must complete in under 3 seconds for typical processes
  - Simulation must run at configurable speeds (from slower-than-real-time to 10x acceleration)
  - Fault detection latency must be under 50ms in runtime
  - The system must handle process definitions with up to 500 steps
  - Memory footprint must not exceed 200MB for the toolkit core

- **Integration Points**
  - Equipment control interfaces (major vendor protocols like OPC UA, Profinet, EtherCAT)
  - Manufacturing Execution Systems (MES) for workflow orchestration
  - Quality Management Systems (QMS) for inspection rule integration
  - Product Lifecycle Management (PLM) systems for process versioning
  - Enterprise Resource Planning (ERP) systems for material and scheduling information

- **Key Constraints**
  - Must operate in isolated networks with limited connectivity
  - Must support deterministic execution for real-time manufacturing
  - Must handle both discrete and continuous process models
  - Must maintain backward compatibility with existing process definitions
  - Must comply with industrial safety standards (IEC 61508/61511)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. The visual process flow designer should be implemented as a programmatic model that could later be connected to a UI, not as a UI component itself.

## Core Functionality

The core functionality of the Manufacturing Process Language Toolkit encompasses:

1. **Process Definition Language**
   - Domain-specific syntax for manufacturing operations and workflows
   - Equipment control abstractions for vendor-agnostic process definitions
   - Quality check specification language for in-process inspection
   - Timing and synchronization constructs for multi-equipment coordination
   - Resource allocation and management declarations

2. **Process Compilation System**
   - Translation of DSL process definitions to executable control instructions
   - Static analysis ensuring process validity and constraint compliance
   - Optimization for efficient execution on target equipment
   - Code generation for multiple equipment control systems

3. **Simulation Engine**
   - Physics-based modeling of manufacturing operations
   - Virtual equipment implementations with realistic behavior
   - Process visualization data generation (for external visualization tools)
   - Timing analysis with critical path identification
   - Resource utilization and bottleneck detection

4. **Fault Detection and Recovery Framework**
   - Pattern matching system for anomaly detection
   - Declarative recovery strategy definitions
   - Fault escalation and notification workflow
   - Historical fault analysis and prediction
   - Production impact assessment for detected faults

5. **Constraint Management System**
   - Equipment capability modeling and limitation tracking
   - Process validation against physical and operational constraints
   - Constraint violation detection with detailed diagnostics
   - Constraint inheritance and composition for complex equipment
   - Runtime constraint monitoring for equipment protection

## Testing Requirements

- **Key Functionalities to Verify**
  - Process definition parsing and validation
  - Equipment abstraction and vendor-specific code generation
  - Process simulation accuracy compared to real-world benchmarks
  - Fault detection and recovery effectiveness
  - Constraint validation correctness for different equipment types

- **Critical User Scenarios**
  - Process engineer defining a new assembly sequence
  - Testing a process via simulation before deployment
  - Integrating new equipment into existing processes
  - Handling common manufacturing faults with recovery patterns
  - Optimizing processes for throughput while maintaining quality

- **Performance Benchmarks**
  - Process compilation: < 3 seconds for 100-step processes
  - Simulation speed: > 10x real-time for standard processes
  - Memory usage: < 200MB for toolkit core components
  - Fault detection: < 50ms from fault condition to detection
  - Constraint validation: < 1 second for full process validation

- **Edge Cases and Error Conditions**
  - Handling incomplete or ambiguous process definitions
  - Managing conflicting equipment control instructions
  - Degraded mode operation when equipment capabilities are reduced
  - Recovery from simulation state corruption
  - Handling of unrealistic or physically impossible process requests

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage for all modules
  - 100% coverage of constraint validation logic
  - Complete coverage of all fault pattern definitions
  - All process definition language constructs must be tested
  - Full path coverage for critical fault recovery workflows

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Manufacturing engineers can define complete process workflows without writing traditional code
2. All defined processes can be simulated with 90% accuracy compared to real-world execution
3. The system correctly validates processes against equipment constraints with no false negatives
4. Fault detection and recovery mechanisms handle at least 95% of common manufacturing exceptions
5. The toolkit integrates with at least three major equipment vendor control systems
6. Process definitions are portable across different manufacturing lines with similar equipment
7. The test suite validates all core functionality with at least 90% coverage
8. Performance benchmarks are met under specified load conditions

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
uv run pytest tests/test_process_compiler.py::test_equipment_abstraction

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into manufacturing systems rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs, with clear separation between the DSL processing logic and any future visualization or UI components.