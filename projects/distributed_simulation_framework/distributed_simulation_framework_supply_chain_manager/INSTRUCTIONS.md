# Global Supply Chain Resilience Simulation Framework

## Overview
A distributed simulation framework specialized for supply chain managers to model and optimize complex global supply chains under various disruption scenarios. The framework enables end-to-end supply chain simulation across manufacturing, warehousing, and transportation with capabilities for testing resilience strategies and developing effective contingency plans.

## Persona Description
Leila manages global supply chain operations requiring optimization across manufacturing, warehousing, and transportation. Her primary goal is to simulate end-to-end supply chains under various disruption scenarios to develop resilient logistics strategies and contingency plans.

## Key Requirements

1. **Multi-Echelon Inventory Optimization**  
   Implement sophisticated inventory modeling and optimization capabilities across multiple supply chain tiers with differentiated policies for various product categories and locations. This capability is critical for Leila because effective inventory management across distributed global networks directly impacts both service levels and working capital, and optimizing inventory placement and quantities throughout the network is fundamental to both cost-efficiency and disruption resilience.

2. **Disruption Scenario Modeling with Recovery Simulation**  
   Develop robust systems for defining, executing, and analyzing a wide range of supply chain disruption scenarios with realistic propagation effects and recovery dynamics. This feature is vital because supply chains face numerous potential disruptions (natural disasters, geopolitical events, supplier failures), and Leila needs to understand precisely how these disruptions would impact operations and how quickly the network could recover with different resilience strategies.

3. **Transportation Network Optimization with Cost Modeling**  
   Create detailed transportation modeling capabilities that optimize routing, mode selection, and carrier allocation while accounting for costs, capacities, lead times, and reliability factors. This functionality is essential because transportation represents a major cost component and constraint in global supply chains, and Leila needs to balance service requirements against transportation expenses while ensuring network resilience.

4. **Supplier Reliability Simulation with Alternative Sourcing**  
   Build supplier performance modeling with capabilities for simulating reliability variations, capacity constraints, and quality issues alongside alternative sourcing strategies. This capability enables Leila to quantify the risks associated with different supplier configurations and develop effective multi-sourcing strategies that balance cost, performance, and resilience considerations.

5. **Just-in-Time vs Buffer Stock Strategy Evaluation**  
   Implement framework for comparing different inventory and production scheduling strategies ranging from just-in-time approaches to strategic buffer stock policies under various demand and supply conditions. This feature is important because the tradeoff between lean operations and resilience buffer is central to modern supply chain management, and data-driven evaluation helps Leila optimize this balance across different product categories and market conditions.

## Technical Requirements

### Testability Requirements
- All optimization algorithms must be verifiable against known optimal solutions for test cases
- Simulation models must be validatable against historical supply chain performance data
- Disruption impact predictions must be measurable against documented historical events
- Transportation and logistics models must produce results consistent with industry benchmarks
- Inventory policy comparisons must show statistical significance in performance differences

### Performance Expectations
- Must support end-to-end modeling of supply chains with at least 1,000 nodes and 10,000 product SKUs
- Should simulate at least 1 year of daily operations within 10 minutes of computation time
- Must efficiently handle at least 100 parallel disruption scenario evaluations
- Should process optimization problems involving 10,000+ variables within reasonable timeframes
- Result analysis should complete within minutes for complex global networks

### Integration Points
- Data interfaces for importing supply chain network definitions
- API for customizing supplier behavior and performance patterns
- Extension points for specialized logistics cost functions
- Connectors for external demand forecast data
- Export capabilities for resilience metrics and optimized strategies

### Key Constraints
- Implementation must be in Python with no UI components
- Memory usage must be optimized for large-scale network simulations
- System must be deterministic with fixed random seeds for reproducibility
- Computation must be distributable across available computing resources
- Data structures must support efficient serialization for checkpointing

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Global Supply Chain Resilience Simulation Framework needs to implement these core capabilities:

1. **Supply Chain Network Modeling**
   - Comprehensive representation of multi-echelon networks
   - Facility modeling with capacity constraints
   - Transportation link definition with mode characteristics
   - Supplier modeling with performance attributes
   - Product hierarchy with bill of materials support

2. **Inventory Management System**
   - Multi-echelon inventory policy implementation
   - Safety stock calculation methodologies
   - Replenishment logic with ordering constraints
   - Stockout handling and backorder processing
   - Inventory cost accounting and carrying charges

3. **Disruption Scenario Engine**
   - Event definition and triggering mechanisms
   - Impact propagation across network nodes
   - Recovery process modeling
   - Contingency plan activation logic
   - Performance degradation and restoration tracking

4. **Transportation Optimization Framework**
   - Mode selection algorithms
   - Route optimization with constraints
   - Carrier selection and allocation
   - Lead time modeling with variability
   - Transportation cost calculation with surcharges

5. **Supplier Performance Simulation**
   - Reliability modeling with stochastic elements
   - Capacity constraint implementation
   - Quality variation effects
   - Lead time distribution modeling
   - Alternative sourcing implementation

6. **Strategy Comparison System**
   - Just-in-time vs. buffer stock policy implementation
   - Performance metric calculation and aggregation
   - Statistical comparison of strategies
   - Sensitivity analysis across scenarios
   - Pareto frontier generation for multi-objective optimization

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of inventory optimization algorithms against benchmark problems
- Realism of disruption propagation through supply chain networks
- Correctness of transportation cost and service level calculations
- Fidelity of supplier performance modeling compared to historical data
- Effectiveness of strategy comparison metrics in identifying optimal approaches
- Performance scaling with supply chain size and complexity

### Critical User Scenarios
- Optimizing inventory placement across a global distribution network
- Simulating the impact of a major supplier failure and evaluating recovery strategies
- Analyzing transportation mode selection tradeoffs between air, ocean, and ground
- Comparing single-sourcing versus multi-sourcing approaches for critical components
- Evaluating just-in-time versus buffer stock strategies under volatile demand
- Developing contingency plans for seasonal demand peaks and supply disruptions

### Performance Benchmarks
- Simulation speed: processing 365 days of operations for 1,000-node network within 10 minutes
- Optimization performance: solving multi-echelon inventory problems with 10,000 SKUs within 30 minutes
- Scaling efficiency: minimum 80% parallel efficiency when scaling from 10 to 100 cores
- Memory usage: maximum 8GB for simulating complex global networks
- Scenario throughput: evaluating 100 disruption scenarios within 1 hour

### Edge Cases and Error Conditions
- Handling of complete supplier failures with no immediate alternatives
- Management of extreme demand spikes beyond all capacity constraints
- Detection of infeasible network configurations
- Recovery from cascading disruptions affecting multiple network nodes
- Adaptation to fundamental changes in supply chain structure

### Test Coverage Requirements
- Unit test coverage of at least 90% for all optimization algorithms
- Integration tests for end-to-end supply chain workflows
- Verification against historical performance data where available
- Performance tests for scaling behavior
- Validation of disruption models against documented historical events

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

The implementation of the Global Supply Chain Resilience Simulation Framework will be considered successful when:

1. The system can accurately model and optimize inventory across multiple supply chain echelons
2. Disruption scenarios realistically propagate through the network with appropriate recovery dynamics
3. Transportation network optimization produces cost-effective solutions that meet service requirements
4. Supplier reliability simulation effectively models performance variations and alternative sourcing strategies
5. Strategy comparison capabilities enable data-driven decisions on just-in-time versus buffer stock approaches

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