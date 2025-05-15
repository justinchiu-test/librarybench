# Manufacturing Process Definition Language Toolkit

## Overview
A specialized Domain Specific Language toolkit designed for defining, simulating, and executing manufacturing processes and quality control workflows. This toolkit empowers process engineers to create precise manufacturing instructions, quality checks, and error handling procedures without requiring programming expertise, while ensuring compatibility with automated equipment.

## Persona Description
Marcus designs automated manufacturing processes for an automotive company with complex assembly lines and quality control. His primary goal is to develop a language that allows process engineers to define manufacturing workflows and quality checks without requiring deep programming knowledge.

## Key Requirements
1. **Visual process flow designer that generates executable DSL code**: A library that can translate between graphical process representations and the underlying DSL code. This is critical because process engineers are accustomed to designing with flow diagrams, and this feature allows them to leverage familiar visual tools while still generating standardized, executable process definitions.

2. **Equipment-specific control syntax with vendor library integration**: Support for specialized commands and parameters unique to different manufacturing equipment vendors, with extensible libraries for common industrial automation systems. This is essential because automotive manufacturing involves diverse specialized equipment from multiple vendors, each with their own control interfaces and parameters.

3. **Simulation environment for testing process definitions**: The ability to run virtual simulations of defined processes before deploying to physical equipment, with detection of timing issues, resource conflicts, and logical errors. This is vital because testing on physical manufacturing lines is costly, time-consuming, and may damage expensive equipment if errors exist in process definitions.

4. **Fault handling pattern library for common manufacturing exceptions**: Pre-defined patterns for handling typical manufacturing issues like part jams, quality deviations, supply interruptions, and equipment malfunctions. This is necessary because robust error handling is critical in automated manufacturing environments where unhandled exceptions can lead to extended production downtime and quality issues.

5. **Physical constraint validation ensuring processes respect equipment limitations**: Validation rules that check if process definitions comply with the physical capabilities of the targeted equipment such as speed limitations, maximum loads, or temperature ranges. This is crucial because definitions that exceed equipment capabilities can cause premature wear, damage to expensive machinery, or safety hazards.

## Technical Requirements
- **Testability Requirements**:
  - Each process definition must be automatically verifiable against equipment constraints
  - Simulation tests must confirm timing, resource utilization, and logical correctness
  - Error handling scenarios must be testable without requiring physical equipment
  - Performance tests must validate process execution within required cycle times
  - All components must achieve at least 90% test coverage

- **Performance Expectations**:
  - Process compilation must complete in under 5 seconds for complex multi-stage processes
  - Simulation must run at least 10x faster than real-time execution
  - Full validation of a process against constraints must complete in under 30 seconds
  - System must handle process definitions with 1000+ steps without significant performance degradation

- **Integration Points**:
  - Equipment control interfaces (OPC UA, Modbus, Profinet, etc.)
  - Manufacturing Execution Systems (MES) and Enterprise Resource Planning (ERP) systems
  - Quality management systems for defect tracking
  - CAD/CAM systems for product design specifications
  - Programmable Logic Controller (PLC) code generators

- **Key Constraints**:
  - Implementation must be in Python with no UI components
  - All process logic must be expressible through the DSL without requiring custom code
  - Process definitions must be storable as human-readable text files
  - System must not require hardware access for simulation and validation

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Manufacturing Process DSL Toolkit must provide:

1. A domain-specific language parser and interpreter specialized for manufacturing processes
2. A translational layer between visual process designs and DSL code
3. Vendor-specific command libraries for various equipment types
4. A process simulation engine that can identify potential execution issues
5. Comprehensive fault handling patterns for manufacturing exceptions
6. A constraint validation system to check equipment limitations
7. Execution time and resource requirement calculators
8. Code generation for deployment to industrial control systems
9. Documentation generators that produce operator instructions
10. Test utilities for verifying process correctness in simulation

The system should enable process engineers to define elements such as:
- Sequential and parallel operation steps
- Quality inspection points with pass/fail criteria
- Material handling and tool change operations
- Process timing and synchronization
- Equipment configuration parameters
- Error detection and recovery procedures
- Process variations based on product specifications
- Resource requirements and utilization

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct translation between visual process designs and executable DSL code
  - Accurate simulation of process execution including timing
  - Proper detection of constraint violations and physical limitations
  - Comprehensive handling of common fault scenarios
  - Correct generation of equipment-specific control commands

- **Critical User Scenarios**:
  - Process engineer creates a new assembly sequence for a vehicle component
  - Quality engineer adds inspection points to an existing process
  - Automation engineer validates a process against new equipment specifications
  - Process optimization to reduce cycle time while maintaining quality
  - Error recovery procedures for handling part variations and equipment faults

- **Performance Benchmarks**:
  - Parse and compile a 500-step process in under 10 seconds
  - Simulate a full vehicle assembly process (5000+ steps) in under 5 minutes
  - Validate constraints for a complete production line in under 60 seconds
  - Generate equipment-specific code for 10 different controller types in under 3 minutes

- **Edge Cases and Error Conditions**:
  - Handling of cyclic process dependencies
  - Graceful degradation when simulation complexity exceeds computational resources
  - Detection of subtle timing issues in parallel operations
  - Identification of resource conflicts in complex multi-product lines
  - Validation of processes spanning multiple interconnected equipment systems

- **Required Test Coverage Metrics**:
  - Minimum 90% code coverage across all modules
  - 100% coverage of DSL parser and interpreter
  - 100% coverage of constraint validation logic
  - 95% coverage of simulation engine components

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
3. The system demonstrates the ability to define real-world manufacturing processes
4. Process simulations accurately predict execution timing and resource utilization
5. Constraint validation correctly identifies violations of equipment capabilities
6. Fault handling patterns appropriately address common manufacturing exceptions
7. The DSL syntax is accessible to process engineers without programming expertise
8. Processes defined in the DSL can be correctly translated to equipment control instructions

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