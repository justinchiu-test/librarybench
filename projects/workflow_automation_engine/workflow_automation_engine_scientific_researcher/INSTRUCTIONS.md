# Experimental Workflow Automation Engine for Scientific Research

## Overview
A specialized workflow automation engine designed for scientific researchers, enabling the orchestration of computational experiments with parameter sweep automation, comprehensive metadata capture, resource optimization, result visualization, and reproducibility packaging. This system provides reliable automation for complex experimental workflows while ensuring scientific reproducibility and efficient resource utilization.

## Persona Description
Dr. Chen conducts computational experiments that involve multiple processing steps and parameter variations. He needs to automate experiment workflows while tracking results and computational environments for reproducibility.

## Key Requirements
1. **Parameter Sweep Automation**: Implement a system for executing workflows across multiple configuration combinations. This feature is critical for Dr. Chen because his research requires testing hypotheses across hundreds of parameter combinations, and manual execution would be prohibitively time-consuming and error-prone.

2. **Experiment Metadata Capture**: Develop comprehensive recording of all inputs, environments, and execution details. Dr. Chen needs this capability because rigorous scientific methodology requires complete documentation of experimental conditions to validate results and enable peer review and replication of his research.

3. **Computational Resource Optimization**: Create scheduling for intensive tasks during off-peak hours. This feature is vital for Dr. Chen as he shares computational resources with other researchers, and optimizing resource usage allows him to maximize experimental throughput while minimizing impact on shared infrastructure.

4. **Result Visualization**: Implement automatic generation of plots and dashboards from experimental outputs. Dr. Chen requires this functionality because visualizing complex experimental results helps identify patterns, anomalies, and relationships in the data that might not be apparent in raw numerical outputs.

5. **Reproducibility Packaging**: Build a system for capturing all workflow elements for future replication. This capability is essential for Dr. Chen because scientific advancement depends on the ability of others to reproduce and build upon his findings, requiring complete packaging of code, data, and environment configurations.

## Technical Requirements
- **Testability Requirements**:
  - Parameter sweep logic must be testable with simplified computational models
  - Metadata capture must be verifiable for completeness and accuracy
  - Resource scheduling must be testable through simulated resource availability patterns
  - Visualization generation must be testable with synthetic experimental data
  - Reproducibility packaging must be verifiable through reconstruction tests

- **Performance Expectations**:
  - Parameter sweep controller should efficiently manage at least 1,000 experimental variations
  - Metadata capture should add less than 2% overhead to experimental execution time
  - Resource scheduling should achieve at least 25% improvement in resource utilization
  - Visualization generation should process datasets of at least 10GB within 5 minutes
  - Reproducibility packaging should complete within 10 minutes for typical experiment sizes

- **Integration Points**:
  - Compute cluster scheduling systems (Slurm, PBS, SGE)
  - Scientific computing libraries (NumPy, SciPy, Pandas)
  - Data storage systems (local filesystems, HPC storage, object stores)
  - Visualization libraries (Matplotlib, Plotly, Seaborn)
  - Version control systems for code tracking
  - Container technologies (Docker, Singularity) for environment capture

- **Key Constraints**:
  - All functionality must be implemented as libraries and APIs, not as applications with UIs
  - System must operate in environments with restricted internet access
  - Must support both interactive and batch execution modes
  - Must handle computational tasks with extreme duration variations (seconds to weeks)
  - Must operate within security constraints of research computing environments
  - Package sizes must be manageable for typical research data sharing platforms

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this Experimental Workflow Automation Engine centers around reproducible scientific experiment orchestration:

1. **Experiment Definition System**: A Python API and YAML/JSON parser for defining computational experiments with parameter spaces, processing steps, and expected outputs.

2. **Parameter Sweep Controller**: Components that efficiently generate and manage experimental variations across multidimensional parameter spaces, with appropriate distribution across available resources.

3. **Metadata Collection Framework**: A comprehensive system for capturing all relevant experimental details, including code versions, input parameters, environmental conditions, and execution timestamps.

4. **Resource Scheduling Optimizer**: Modules that analyze resource availability patterns and schedule computational tasks to maximize throughput while minimizing interference with other users.

5. **Results Management System**: Components for organizing, indexing, and retrieving experimental outputs based on parameter values and execution conditions.

6. **Visualization Engine**: A flexible system for automatically generating appropriate visualizations based on experiment type, output data characteristics, and common scientific plotting conventions.

7. **Reproducibility Packager**: Modules that gather all necessary components (code, data, environment definitions, parameters) to enable exact reproduction of experimental results by other researchers.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Experiment definition and validation
  - Parameter space generation and traversal
  - Complete and accurate metadata collection
  - Effective resource allocation and scheduling
  - Appropriate visualization selection and generation
  - Comprehensive reproducibility package creation and restoration

- **Critical User Scenarios**:
  - Full parameter sweep across multidimensional parameter space
  - Execution of long-running computational experiment with checkpointing
  - Resource-adaptive scheduling during periods of varying availability
  - Visualization generation for diverse result types
  - Creation and validation of reproducibility packages
  - Reconstruction of experimental conditions from metadata

- **Performance Benchmarks**:
  - Parameter space generation for 1,000+ variations within 10 seconds
  - Metadata capture overhead less than 2% of execution time
  - Resource utilization improvement of at least 25% through intelligent scheduling
  - Visualization generation for 10GB datasets within 5 minutes
  - Reproducibility packaging completed within 10 minutes for typical experiment sizes

- **Edge Cases and Error Conditions**:
  - Parameter combinations generating invalid experiment configurations
  - Partial experiment completion due to resource limitations
  - Recovery from node failures during long-running experiments
  - Handling of extremely large output datasets
  - Managing parameter spaces with mixed data types
  - Preserving reproducibility with external dependencies
  - Resource contention during peak usage periods
  - Visualization of unusual or unexpected result distributions

- **Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for parameter sweep logic
  - 100% coverage for metadata collection
  - 100% coverage for reproducibility packaging functionality
  - All error handling paths must be tested

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
A successful implementation of the Experimental Workflow Automation Engine will meet the following criteria:

1. Parameter sweep system that correctly generates and executes experiment variations across multidimensional parameter spaces, verified by tests with various parameter configurations.

2. Comprehensive metadata capture that records all relevant experimental details, confirmed through validation of captured metadata for completeness.

3. Resource scheduling optimization that improves utilization of computational resources, demonstrated by comparative performance tests.

4. Automated visualization generation that appropriately represents different types of experimental results, validated with diverse synthetic datasets.

5. Reproducibility packaging that enables exact replication of experimental conditions, verified through reconstruction tests.

6. Performance meeting or exceeding the specified benchmarks for efficiency, overhead, and processing capability.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Project Setup Instructions
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

4. Install test dependencies:
   ```
   pip install pytest pytest-json-report
   ```

CRITICAL REMINDER: It is MANDATORY to run the tests with pytest-json-report and provide the pytest_results.json file as proof of successful implementation:
```
pytest --json-report --json-report-file=pytest_results.json
```