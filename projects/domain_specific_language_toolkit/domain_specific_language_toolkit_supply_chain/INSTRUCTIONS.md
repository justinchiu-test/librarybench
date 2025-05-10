# Supply Chain Constraint Definition Language

A domain-specific language toolkit for expressing shipping rules, inventory policies, and optimization goals for complex logistics networks.

## Overview

This project provides a comprehensive framework for developing domain-specific languages focused on supply chain optimization. It enables logistics planners to express shipping rules, inventory policies, and optimization goals without requiring knowledge of mathematical optimization techniques. The system emphasizes multi-objective optimization, constraint visualization, transportation network modeling, inventory policy templates, and scenario comparison.

## Persona Description

Raj develops logistics planning systems for a global retail operation with complex supply chains. His primary goal is to create a constraint definition language that allows logistics planners to express shipping rules, inventory policies, and optimization goals without requiring knowledge of mathematical optimization techniques.

## Key Requirements

1. **Multi-objective optimization goal definition with priority weighting**
   - Implement a system for defining and balancing multiple competing objectives in supply chain optimization
   - This capability is essential for Raj because real-world logistics problems rarely have single objectives. Supply chains must simultaneously optimize for cost, speed, reliability, and sustainability, among other factors. This feature enables planners to express complex trade-offs between competing goals using business terminology rather than mathematical formulations.

2. **Constraint visualization showing impact on solution space**
   - Develop a data representation system that can visualize how logistics constraints affect the available solution space
   - Understanding the impact of constraints is critical for effective optimization. This feature helps Raj's logistics planners visualize how each constraint (e.g., delivery time windows, capacity limits) restricts possible solutions, allowing them to identify overly restrictive constraints and understand optimization results.

3. **Transportation network modeling with route constraint definition**
   - Create a modeling framework for defining transportation networks and route-specific constraints
   - Supply chains operate across complex networks with varying transportation options. This capability allows Raj to model the specific characteristics of different routes and transportation modes, including capacity, cost, time, reliability, and availability constraints, enabling more realistic and effective optimization.

4. **Inventory policy templates for common management strategies**
   - Build a library of predefined inventory policy templates that encapsulate common inventory management strategies
   - Inventory policies significantly impact overall supply chain performance. This feature provides Raj's planners with ready-to-use templates for strategies like safety stock calculations, reorder point determination, or ABC classification, allowing them to implement sophisticated inventory management without specialized knowledge.

5. **Scenario comparison tools for evaluating rule modifications**
   - Implement analytical tools for comparing optimization outcomes across different constraint scenarios
   - Supply chain planning requires frequent evaluation of "what-if" scenarios. This capability enables Raj's team to systematically compare the effects of different constraints or rule modifications, supporting data-driven decision making about supply chain design and operational policies.

## Technical Requirements

### Testability Requirements
- Optimization models must be testable with historical supply chain data
- Constraint definitions must be verifiable against known feasible solutions
- Inventory policies must be testable with simulated demand patterns
- Transportation networks must be validatable against actual route data
- Test coverage must include both typical and edge case supply chain scenarios

### Performance Expectations
- Constraint compilation must complete within 5 seconds for complex supply chains
- Optimization problem solving must scale to networks with 1000+ nodes
- Scenario comparison must process 10+ alternative constraint sets within 2 minutes
- Visualization data generation must complete within 10 seconds for large networks
- The system must support concurrent evaluation of multiple supply chain configurations

### Integration Points
- Enterprise resource planning (ERP) systems for master data
- Transportation management systems (TMS) for route information
- Warehouse management systems (WMS) for inventory data
- Demand forecasting systems for planning inputs
- Business intelligence platforms for result reporting

### Key Constraints
- No UI components; all visualization capabilities must be expressed through data
- All optimization models must be deterministic and reproducible
- The system must handle real-world scale supply chain problems
- All functionality must be accessible via well-defined APIs
- The system must support both strategic planning and operational execution

## Core Functionality

The system must provide a framework for:

1. **Constraint Definition Language**: A grammar and parser for defining supply chain constraints, objectives, and policies in business terminology.

2. **Multi-objective Optimization**: Mechanisms for expressing and balancing multiple competing objectives with explicit priority settings.

3. **Transportation Network Modeling**: Tools for representing transportation networks with node, link, and route-specific constraints.

4. **Inventory Policy Management**: Frameworks for defining inventory management rules, safety stock policies, and replenishment strategies.

5. **Constraint Visualization**: Systems for representing constraints and their impacts in a form suitable for visualization.

6. **Scenario Analysis**: Methods for comparing outcomes across different constraint configurations to support decision making.

7. **Optimization Compilation**: Translation of high-level constraint definitions into mathematical optimization problems.

8. **Solution Interpretation**: Tools for translating optimization solutions back into business-relevant recommendations.

## Testing Requirements

### Key Functionalities to Verify
- Accurate parsing of constraint definitions from domain-specific syntax
- Correct formulation of multi-objective optimization problems
- Proper modeling of transportation networks and route constraints
- Effective implementation of inventory policy templates
- Reliable comparison of results across different scenario configurations

### Critical User Scenarios
- Logistics planner defines constraints for a global supply chain
- System balances multiple competing optimization objectives based on priorities
- Transportation network is modeled with route-specific constraints
- Inventory policies are applied across distribution network
- Multiple constraint scenarios are compared to evaluate policy changes

### Performance Benchmarks
- Constraint compilation completed in under 5 seconds for complex definitions
- Optimization models solved within reasonable time frames based on problem size
- Scenario comparison processing 10+ alternatives within 2 minutes
- Visualization data generation completed in under 10 seconds
- System maintains performance with supply chains containing 1000+ nodes

### Edge Cases and Error Conditions
- Handling of infeasible constraint combinations
- Proper response to conflicting optimization objectives
- Graceful degradation when optimizing extremely large networks
- Recovery from partial constraint compilation failures
- Handling of incomplete or uncertain supply chain data

### Required Test Coverage Metrics
- Minimum 90% line coverage for core constraint parsing and compilation logic
- 100% coverage of multi-objective optimization algorithms
- 95% coverage of transportation network modeling functions
- 90% coverage for inventory policy implementations
- 100% test coverage for scenario comparison calculations

## Success Criteria

The implementation will be considered successful when:

1. Logistics planners can define complex supply chain constraints without requiring knowledge of mathematical optimization.

2. The system successfully balances multiple competing objectives according to business priorities.

3. Transportation networks and route constraints are accurately modeled and optimized.

4. Inventory policies consistently yield expected results across various demand patterns.

5. Scenario comparison provides clear insights into the effects of constraint modifications.

6. The time required to define and solve supply chain optimization problems is reduced by at least 60%.

7. All test requirements are met with specified coverage metrics and performance benchmarks.

8. Optimization results lead to measurable improvements in supply chain performance metrics such as cost, service level, and inventory efficiency.

To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.