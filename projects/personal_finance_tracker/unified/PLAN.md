# Refactoring Plan for Unified Financial Library

This document outlines the architecture, design, and implementation plan for creating a unified library that serves both freelancer financial management and ethical investment tracking needs.

## 1. Analysis of Common Patterns

After examining both implementations, I've identified several common patterns and abstractions that can be unified:

### 1.1 Common Data Structures

1. **Transaction models**: Both implementations have transaction models for tracking financial activities.
2. **Category models**: Both use categorization systems (expenses vs. ethical categories).
3. **Date-based financial data**: Both track financial data over time periods.
4. **Audit and tracking**: Both implement tracking of changes for accountability.

### 1.2 Common Algorithms

1. **Categorization engines**: Both implement rule-based categorization systems.
2. **Scoring and evaluation**: Both use scoring mechanisms (profitability vs. ethical scoring).
3. **Time-series analysis**: Both analyze financial data across time.
4. **Summary and reporting**: Both generate summaries of financial data.

### 1.3 Common Utilities

1. **Data validation**: Both validate input data with constraints.
2. **Performance measurement**: Both track execution time for operations.
3. **Caching mechanisms**: Both implementations use caching for performance.
4. **Date manipulation**: Both work with date ranges and periods.

## 2. Core Architecture

The unified library will follow this architecture:

```
common/
├── core/
│   ├── models/          # Shared data models
│   ├── categorization/  # Classification and categorization
│   ├── analysis/        # Financial analysis algorithms
│   ├── reporting/       # Reporting and summarization
│   └── utils/           # Shared utilities
```

### 2.1 Core Components and Responsibilities

1. **Models**
   - Base transaction model
   - Category interface
   - Time entry tracking
   - Financial entity models (accounts, portfolios)
   - Validation framework

2. **Categorization**
   - Generic rule engine
   - Category mapping and matching
   - Confidence scoring
   - Audit trail management

3. **Analysis**
   - Time-series calculations
   - Financial metrics computation
   - Projection algorithms
   - Scoring and evaluation framework

4. **Reporting**
   - Summary generation
   - Time-period reporting
   - Data aggregation utilities

5. **Utilities**
   - Date manipulation helpers
   - Performance tracking
   - Caching utilities
   - Validation helpers

### 2.2 Interface Definitions

Key interfaces will be defined for:

1. **Categorizable**: Interface for items that can be categorized
2. **Rule**: Interface for categorization rules
3. **TimeTracked**: Interface for items that exist over a time period
4. **Analyzable**: Interface for items that can be analyzed
5. **Auditable**: Interface for items that maintain an audit trail

## 3. Extension Points

The unified library will provide extension points for persona-specific functionality:

1. **Category system extensions**: Allow domain-specific category implementations
2. **Custom rules**: Framework for specialized categorization rules
3. **Analysis extensions**: Pluggable analysis algorithms
4. **Custom validations**: Domain-specific validation rules
5. **Specialized reporting**: Extended reporting capabilities

## 4. Migration Strategy

### 4.1 Freelancer Implementation Migration

1. Move common models to `common.core.models`
2. Refactor categorizer to use common rule engine
3. Adapt income smoothing to use common time-series analysis
4. Migrate tax calculations to use common financial analysis
5. Update profitability analyzer to use common reporting

### 4.2 Ethical Finance Implementation Migration

1. Move ESG models to `common.core.models`
2. Adapt screening to use common categorization engine
3. Refactor impact measurement to use common analysis framework
4. Update portfolio analysis to use common reporting
5. Migrate values budgeting to use common categorization

## 5. Implementation Plan

### Phase 1: Core Models and Utilities

1. Implement base data models (Transaction, Category, TimeEntry)
2. Create shared validation utilities
3. Implement common date and time utilities
4. Create base interfaces for extensibility

### Phase 2: Categorization Framework

1. Implement generic rule engine
2. Create base categorizer class
3. Implement audit trail system
4. Add performance tracking

### Phase 3: Analysis Framework

1. Implement time-series analysis utilities
2. Create financial calculation helpers
3. Add projection and forecasting base classes
4. Implement scoring and evaluation framework

### Phase 4: Reporting and Integration

1. Create summary reporting framework
2. Implement data aggregation utilities
3. Add export/import capabilities
4. Create integration tests

### Phase 5: Persona Implementation Migration

1. Refactor freelancer implementation to use common library
2. Refactor ethical finance implementation to use common library
3. Verify all tests pass for both implementations
4. Optimize performance bottlenecks

## 6. Testing Strategy

1. Create unit tests for all common components
2. Maintain existing persona-specific tests
3. Add integration tests between common and persona-specific code
4. Verify performance requirements are met
5. Test edge cases and error handling

## 7. Design Decisions

### 7.1 Model Implementation

For data models, we'll use Pydantic for the freelancer implementation and adapt the dataclass approach from ethical finance to work with it. This provides us with validation, serialization, and better type safety.

### 7.2 Categorization Approach

The categorization system will use a strategy pattern, allowing different categorization algorithms to be plugged in while maintaining a consistent interface.

### 7.3 Analysis Framework

The analysis framework will separate data retrieval, calculation, and presentation, allowing each implementation to customize as needed while sharing core algorithms.

### 7.4 Extensibility vs. Simplicity

We'll prioritize a clean, simple API surface while providing extension points for specialized functionality. This balances code reuse with flexibility.

### 7.5 Performance Considerations

We'll implement caching, lazy evaluation, and performance monitoring to ensure the unified library meets or exceeds the performance of the original implementations.

## 8. Conclusion

This refactoring plan creates a unified library that extracts common functionality while preserving the specialized features of each persona's implementation. The approach focuses on clean interfaces, appropriate abstractions, and maintainable code organization.