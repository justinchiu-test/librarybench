# Supply Chain Optimization Language Toolkit

## Overview
A specialized Domain Specific Language toolkit for defining, analyzing, and optimizing complex supply chain constraints and operations. This toolkit enables logistics planners to express sophisticated shipping rules, inventory policies, and optimization goals without requiring knowledge of mathematical optimization techniques, while providing powerful analysis and simulation capabilities.

## Persona Description
Raj develops logistics planning systems for a global retail operation with complex supply chains. His primary goal is to create a constraint definition language that allows logistics planners to express shipping rules, inventory policies, and optimization goals without requiring knowledge of mathematical optimization techniques.

## Key Requirements
1. **Multi-objective optimization goal definition with priority weighting**: The ability to define multiple, potentially competing optimization objectives (cost reduction, delivery speed, inventory minimization, etc.) with explicit priority weights and trade-off parameters. This is critical because real-world supply chain optimization rarely has a single goal, and the ability to balance multiple objectives with appropriate priorities allows logistics planners to align optimization with strategic business goals.

2. **Constraint visualization showing impact on solution space**: Visual analysis tools that demonstrate how each constraint affects the solution space, identifying which constraints are most restrictive and where relaxation might yield significant benefits. This is essential because understanding constraint impacts helps planners focus improvement efforts on the most limiting factors and communicate the reasons for suboptimal solutions to stakeholders.

3. **Transportation network modeling with route constraint definition**: Capabilities to model complex transportation networks with multi-modal options (road, rail, sea, air) and define constraints for routes including capacity limitations, transit times, availability windows, and cost structures. This is vital because transportation is typically the largest cost component in supply chains, and accurate modeling of network constraints enables significant cost savings and service improvements.

4. **Inventory policy templates for common management strategies**: Pre-defined templates for standard inventory management approaches (economic order quantity, safety stock, min-max, etc.) that can be customized with specific parameters and business rules. This is necessary because inventory management is complex and mathematically sophisticated, and templates allow logistics planners to implement best-practice approaches without requiring expertise in inventory theory.

5. **Scenario comparison tools for evaluating rule modifications**: Simulation and analysis capabilities to compare the outcomes of different constraint configurations across multiple scenarios (normal operations, peak season, disruption events, etc.). This is crucial because understanding how rule changes might affect performance under various conditions is essential for risk management and resilience planning, helping planners make informed decisions about policy changes.

## Technical Requirements
- **Testability Requirements**:
  - Each optimization model must be automatically verifiable for mathematical consistency
  - Constraint definitions must be testable against known feasible and infeasible solutions
  - Inventory policy implementations must be validated against theoretical optimal values
  - Scenario comparisons must produce consistent results with controlled variations
  - All components must achieve at least 90% test coverage

- **Performance Expectations**:
  - Optimization problem compilation must complete in under 10 seconds for large models
  - Solution computation must handle problems with 10,000+ variables in reasonable time
  - Constraint visualization must generate results for complex models in under 30 seconds
  - Scenario comparison must process 50+ scenarios in under 10 minutes

- **Integration Points**:
  - Transportation management systems
  - Warehouse management systems
  - Enterprise resource planning (ERP) platforms
  - Demand forecasting systems
  - Supplier management databases
  - Real-time tracking and IoT data sources

- **Key Constraints**:
  - Implementation must be in Python with no UI components
  - All optimization logic must be expressible through the DSL without requiring custom code
  - Constraint definitions must be storable as human-readable text files
  - System must leverage existing optimization solvers (CPLEX, Gurobi, etc.) as backends
  - Performance must scale to enterprise-level supply chain complexity

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Supply Chain Optimization DSL Toolkit must provide:

1. A domain-specific language parser and interpreter specialized for supply chain constraints
2. Multi-objective optimization definition with priority weighting mechanisms
3. Constraint visualization and impact analysis tools
4. Transportation network modeling capabilities
5. Inventory policy template implementations
6. Scenario generation and comparison utilities
7. Integration with mathematical optimization solvers
8. Performance analysis and solution quality assessment
9. Documentation generators for logistics planning teams
10. Test utilities for validating constraint models

The system should enable logistics planners to define elements such as:
- Facility location constraints and capacities
- Transportation routes, modes, and schedules
- Inventory policies and storage limitations
- Service level requirements and delivery timeframes
- Cost structures and budget constraints
- Supplier capabilities and limitations
- Demand patterns and seasonality factors
- Risk management policies and contingency plans

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct parsing of DSL syntax into mathematical optimization models
  - Accurate handling of multi-objective optimization with priority weights
  - Proper visualization of constraint impacts on solution space
  - Correct modeling of transportation networks and routes
  - Accurate implementation of inventory policy templates

- **Critical User Scenarios**:
  - Logistics planner defines multi-objective optimization for peak season planning
  - Network analyst evaluates impact of route constraints on overall costs
  - Inventory manager implements custom safety stock policies across products
  - Supply chain director compares scenarios for potential disruption events
  - Operations researcher identifies constraint relaxations for performance improvement

- **Performance Benchmarks**:
  - Compile and prepare a model with 5000+ variables in under 30 seconds
  - Generate constraint impact visualizations for 100+ constraints in under 60 seconds
  - Evaluate 10+ inventory policy variations across 1000+ SKUs in under 5 minutes
  - Compare 20+ scenarios with different constraint configurations in under 10 minutes

- **Edge Cases and Error Conditions**:
  - Handling of mathematically infeasible constraint combinations
  - Detection of unbounded optimization problems
  - Management of conflicting multi-objective priorities
  - Behavior during transportation network disruptions
  - Graceful degradation when optimization becomes computationally intractable

- **Required Test Coverage Metrics**:
  - Minimum 90% code coverage across all modules
  - 100% coverage of constraint parser and interpreter
  - 100% coverage of multi-objective handling mechanisms
  - 95% coverage of inventory policy implementations

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
3. The system demonstrates the ability to express complex supply chain constraints
4. Multi-objective optimization correctly balances competing priorities
5. Constraint visualization accurately depicts impact on solution space
6. Transportation network modeling correctly represents route constraints
7. Inventory policy templates accurately implement theoretical models
8. Scenario comparison provides meaningful analysis of potential rule modifications

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