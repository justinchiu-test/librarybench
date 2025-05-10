# Supply Chain Constraint Language

A domain-specific language toolkit for defining and solving logistics optimization problems.

## Overview

This project delivers a specialized domain-specific language toolkit that enables logistics planners to express complex supply chain constraints, optimization goals, and business rules without requiring expertise in mathematical optimization or programming. The toolkit translates these domain-specific definitions into executable optimization models, providing powerful supply chain planning capabilities while hiding the underlying complexity of the mathematical solvers.

## Persona Description

Raj develops logistics planning systems for a global retail operation with complex supply chains. His primary goal is to create a constraint definition language that allows logistics planners to express shipping rules, inventory policies, and optimization goals without requiring knowledge of mathematical optimization techniques.

## Key Requirements

1. **Multi-objective optimization goal definition with priority weighting**
   - Essential for Raj because supply chain decisions typically involve multiple competing objectives (cost, service level, sustainability, risk), and planners need to express their relative importance without understanding the underlying mathematical formulations.
   - The DSL must provide intuitive syntax for defining multiple optimization objectives with priority weights, trade-off preferences, and goal hierarchies that can be translated into appropriate objective functions.

2. **Constraint visualization showing impact on solution space**
   - Critical because understanding how business constraints affect potential solutions is vital for planners to make informed decisions, and Raj needs to help them visualize these impacts without requiring mathematical background.
   - The system must analyze defined constraints to determine their impact on the solution space, generating structured data that quantifies constraint effects and identifies binding constraints.

3. **Transportation network modeling with route constraint definition**
   - Vital because global supply chains involve complex transportation networks with varying costs, capacities, and transit times, and planners need to express routing rules and constraints in familiar terms.
   - The DSL must support defining transportation networks, route parameters, modal constraints, and capacity limitations using logistics terminology rather than mathematical notation.

4. **Inventory policy templates for common management strategies**
   - Necessary because inventory management follows established patterns (safety stock, min-max, economic order quantity, etc.), and Raj needs to provide pre-defined templates that planners can customize without redefining common logic.
   - The toolkit must include parameterizable templates for standard inventory policies, allowing planners to select and configure appropriate strategies for different product categories and locations.

5. **Scenario comparison tools for evaluating rule modifications**
   - Important because supply chain planning requires evaluating multiple what-if scenarios with different constraints and parameters, and planners need to understand the impact of potential changes before implementation.
   - The system must support defining and solving multiple planning scenarios with varying constraints, providing comparative analysis of outcomes to support decision-making.

## Technical Requirements

- **Testability Requirements**
  - All constraint definitions must be testable with simulated supply chain data
  - Optimization models must produce deterministic results for identical inputs
  - Constraint binding analysis must be verified against known optimal solutions
  - Scenario comparison must provide consistent, reproducible metrics
  - Performance benchmarks must be validated against industry standards

- **Performance Expectations**
  - Small optimization problems (< 1000 variables) must solve within 10 seconds
  - Medium-sized problems (< 10,000 variables) must solve within 2 minutes
  - Large problems may require distributed processing with appropriate scaling
  - Memory usage must not exceed 2GB for typical supply chain models
  - Optimization status updates must be available for long-running solves

- **Integration Points**
  - Enterprise Resource Planning (ERP) systems for master data
  - Warehouse Management Systems (WMS) for inventory data
  - Transportation Management Systems (TMS) for route information
  - Demand planning systems for forecast integration
  - Business Intelligence (BI) platforms for results visualization

- **Key Constraints**
  - Must support both deterministic and stochastic optimization approaches
  - Must provide explainable results with solution rationale
  - Must handle real-world data imperfections and inconsistencies
  - Must allow manual overrides for planner judgment integration
  - Must operate within corporate IT security frameworks

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. The visualization capabilities should generate structured data that could be visualized by external tools, not implementing the visualization itself.

## Core Functionality

The core functionality of the Supply Chain Constraint Language encompasses:

1. **Constraint Definition Language**
   - Supply chain domain-specific syntax for business rules and limitations
   - Multi-objective specification with prioritization
   - Network flow constraint definition
   - Inventory management rule specification
   - Time-phased planning horizon support

2. **Optimization Model Generator**
   - Translation of DSL constraints to mathematical formulations
   - Solver selection and configuration based on problem characteristics
   - Problem decomposition for large-scale optimization
   - Solution strategy definition and implementation
   - Infeasibility detection and diagnosis

3. **Network Modeling System**
   - Transportation mode and route definition
   - Capacity and cost parameter specification
   - Transit time and reliability modeling
   - Multi-echelon network structure definition
   - Service level constraint implementation

4. **Inventory Policy Framework**
   - Policy template library with parameterization
   - Inventory calculation methods and formulas
   - Safety stock determination algorithms
   - Replenishment trigger rule definition
   - Obsolescence and perishability handling

5. **Scenario Management System**
   - Comparative scenario definition
   - Key performance indicator calculation
   - Scenario analysis and ranking
   - Sensitivity testing methodology
   - Solution robustness evaluation

## Testing Requirements

- **Key Functionalities to Verify**
  - Constraint translation accuracy to mathematical models
  - Optimization solver convergence to validated solutions
  - Network flow modeling correctness for complex routes
  - Inventory policy implementation accuracy
  - Scenario comparison metric calculation

- **Critical User Scenarios**
  - Logistics planner defining multi-objective shipping optimization
  - Supply chain analyst testing network design alternatives
  - Inventory manager implementing new stock policies
  - Operations director comparing different constraint scenarios
  - Business analyst evaluating cost/service trade-offs

- **Performance Benchmarks**
  - Small problems (< 1000 variables): < 10 seconds to optimal solution
  - Medium problems (< 10,000 variables): < 2 minutes to optimal solution 
  - Constraint binding analysis: < 30 seconds for identifying critical constraints
  - Scenario comparison: < 1 minute for comparative analysis of 5 scenarios
  - Model generation: < 5 seconds for translation from DSL to solver format

- **Edge Cases and Error Conditions**
  - Handling infeasible constraint combinations
  - Managing solver convergence failures
  - Addressing inconsistent or contradictory business rules
  - Graceful degradation when optimal solutions cannot be found
  - Handling extremely large networks with computational limitations

- **Required Test Coverage Metrics**
  - Minimum 90% code coverage for all modules
  - 100% coverage of constraint translation logic
  - Complete testing of all inventory policy templates
  - All optimization model generators must be validated
  - Full coverage of scenario comparison algorithms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Logistics planners can define complete optimization problems without mathematical expertise
2. Generated optimization models consistently produce valid, optimal solutions
3. The system correctly identifies and explains binding constraints in business terms
4. Inventory policy templates accurately implement standard management strategies
5. Scenario comparison provides clear, actionable insights into constraint modifications
6. The toolkit integrates with enterprise supply chain systems for data exchange
7. The test suite validates all core functionality with at least 90% coverage
8. Performance benchmarks are met under typical supply chain planning workloads

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
uv run pytest tests/test_constraint_translator.py::test_network_flow_constraints

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

When implementing this project, remember to focus on creating a library that can be integrated into supply chain planning systems rather than a standalone application with user interfaces. All functionality should be exposed through well-defined APIs, with a clear separation between the constraint definition language and any future visualization or UI components.