# Climate System Simulation Framework

## Overview
A distributed simulation framework specialized for climate scientists to model complex regional climate systems with high resolution and computational efficiency. The framework enables integration of atmospheric, oceanic, and land components while efficiently distributing computation across available resources for long-running climate simulations.

## Persona Description
Dr. Zhang models regional climate systems to predict environmental changes and evaluate mitigation strategies. His primary goal is to run high-resolution climate simulations that integrate atmospheric, oceanic, and land components while maximizing computational efficiency.

## Key Requirements

1. **Multi-Physics Domain Integration with Different Timescales**  
   Implement a system for coupling different physical domains (atmosphere, ocean, land, ice) that operate on different timescales while maintaining physical consistency. This feature is critical for Dr. Zhang because realistic climate modeling requires simulating interactions between these systems that evolve at different rates, and accurate coupling is essential for modeling feedback mechanisms that drive climate dynamics.

2. **Uncertainty Quantification through Ensemble Simulations**  
   Develop a framework for automatically generating, managing, and analyzing ensemble simulations with perturbed initial conditions and parameters to quantify prediction uncertainties. This capability is vital because climate projections inherently contain uncertainties, and ensemble methods allow Dr. Zhang to provide statistical confidence intervals for predictions, which are essential for science-based policy decisions.

3. **Downscaling Capabilities for Regional Impact Assessment**  
   Create a system for dynamically downscaling global climate data to high-resolution regional grids while preserving physical consistency and boundary conditions. This feature enables Dr. Zhang to produce detailed local climate projections that decision-makers need for adaptation planning, as regional impacts are what ultimately matter for community resilience strategies.

4. **Long-Running Simulation Management with Incremental Results**  
   Build mechanisms for checkpoint/restart, incremental result analysis, and simulation monitoring for simulations that run for weeks or months of computation time. This capability is essential because climate simulations typically require extremely long run times, and Dr. Zhang needs to monitor progress, analyze interim results, and recover from system failures without losing valuable computation.

5. **Computation Distribution Optimized for Heterogeneous Clusters**  
   Implement intelligent workload distribution that can leverage different types of computing resources (CPU, GPU, specialized hardware) with dynamic load balancing. This feature is crucial because climate centers often have heterogeneous computing environments, and optimal utilization of all available resources is necessary to achieve the highest possible resolution and longest simulation timeframes within resource constraints.

## Technical Requirements

### Testability Requirements
- All components must have deterministic modes for reproducible testing
- Physics modules must be validated against standard benchmark cases
- Domain coupling mechanisms must preserve conservation laws within acceptable tolerances
- Ensemble generation must produce statistically valid parameter variations
- Downscaling algorithms must be verifiable against high-resolution reference data

### Performance Expectations
- Must achieve at least 80% parallel efficiency on up to 1,000 cores for large domains
- Should process at least 5 simulated years per day of computation for standard resolution
- Ensemble simulations should scale linearly with available computational resources
- Downscaling operations should maintain at least 70% of the performance of raw simulation
- Checkpoint/restart overhead should be less than 5% of total computation time

### Integration Points
- Data interfaces compatible with standard climate data formats (NetCDF, GRIB)
- API for defining and registering new physical process models
- Workflow integration with data preprocessing and postprocessing pipelines
- Extension points for custom uncertainty quantification methods
- Interfaces for observational data assimilation

### Key Constraints
- Implementation must be in Python with no UI components
- All core algorithms must be mathematically stable for long-running simulations
- Must operate within memory constraints of typical HPC environments
- Data storage formats must be self-describing and platform-independent
- Must support both MPI and shared-memory parallelism models

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Climate System Simulation Framework needs to implement these core capabilities:

1. **Multi-Domain Physics Engine**
   - Implementation of atmospheric, oceanic, land surface, and cryosphere models
   - Flexible coupling mechanisms between domains with different spatial and temporal scales
   - Conservation enforcement for critical physical quantities (energy, mass, momentum)
   - Support for pluggable physics parameterization schemes

2. **Ensemble Simulation System**
   - Parameter perturbation mechanisms based on physical constraints
   - Efficient execution of multiple simulation instances
   - Statistical analysis tools for ensemble results
   - Uncertainty propagation and quantification

3. **Spatial Resolution Management**
   - Dynamic grid refinement and nested domain support
   - Downscaling algorithms for regional focus areas
   - Boundary condition handling between resolution levels
   - Conservation-preserving interpolation methods

4. **Execution Control Framework**
   - Checkpoint/restart mechanisms with data integrity validation
   - Progress monitoring and early result extraction
   - Fault tolerance and recovery strategies
   - Simulation lifecycle management

5. **Resource Optimization System**
   - Workload distribution based on resource capabilities
   - Dynamic load balancing for heterogeneous environments
   - Memory usage optimization for large-scale simulations
   - I/O patterns optimized for parallel file systems

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of physical process implementations against analytical solutions
- Conservation properties in domain coupling mechanisms
- Statistical properties of ensemble generation methods
- Fidelity of downscaled results compared to high-resolution reference runs
- Correctness of checkpoint/restart functionality for long simulations
- Efficiency of resource utilization in heterogeneous environments

### Critical User Scenarios
- Running a century-scale climate simulation with full Earth system coupling
- Generating a 50-member ensemble to quantify prediction uncertainties
- Downscaling global climate projections to regional domains
- Recovering and continuing a simulation after system failure
- Analyzing incremental results from ongoing simulations
- Deploying a simulation across a heterogeneous computing environment

### Performance Benchmarks
- Scaling efficiency to at least 1,000 cores with minimum 80% parallel efficiency
- Processing speed of at least 5 simulated years per day for standard configurations
- Storage efficiency: maximum 1TB per decade of simulated climate at standard resolution
- Memory footprint: maximum 2GB per core for production simulations
- Checkpoint overhead: less than 5% of total runtime

### Edge Cases and Error Conditions
- Handling of numerical instabilities in physical process calculations
- Recovery from partial or corrupted checkpoint data
- Management of disk space limitations during long simulations
- Detection and reporting of non-physical results
- Graceful degradation when requested resources are unavailable

### Test Coverage Requirements
- Unit test coverage of at least 90% for all physics implementations
- Integration tests for all coupling mechanisms
- Verification against standard benchmark cases from the climate modeling community
- Performance tests covering scaling behavior
- Regression tests for all critical workflows

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

The implementation of the Climate System Simulation Framework will be considered successful when:

1. The system correctly integrates multiple physical domains operating at different timescales while maintaining conservation properties
2. Ensemble simulations successfully quantify uncertainties in climate projections
3. Downscaling operations produce high-resolution regional data consistent with global simulations
4. Long-running simulations can be managed effectively with checkpointing and incremental analysis
5. Computational workloads are efficiently distributed across heterogeneous computing resources

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Environment Setup

To set up the development environment:

1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

The pytest_results.json file must be included as proof that all tests pass and is a critical requirement for project completion.