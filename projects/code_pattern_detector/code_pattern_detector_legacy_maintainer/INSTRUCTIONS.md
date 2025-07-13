# PyPatternGuard - Legacy Code Modernization Analyzer

## Overview
A specialized code pattern detection system for identifying and prioritizing modernization opportunities in legacy codebases. This implementation focuses on detecting outdated patterns, assessing technical debt, estimating refactoring complexity, and generating actionable modernization roadmaps for systematic codebase improvement.

## Persona Description
A senior developer tasked with modernizing a 10-year-old codebase who needs to identify outdated patterns and prioritize refactoring efforts. He requires analysis of technical debt and migration complexity.

## Key Requirements

1. **Deprecated API usage detection with migration path suggestions**
   - Essential for identifying code that relies on outdated or unsupported APIs. Migration path suggestions provide clear next steps, reducing the research burden and accelerating the modernization process.

2. **Technical debt scoring based on pattern age and maintenance cost**
   - Critical for prioritizing refactoring efforts based on business impact. Quantifying technical debt helps justify modernization investments and focus resources on the most problematic areas.

3. **Refactoring effort estimation with dependency impact analysis**
   - Vital for realistic project planning and resource allocation. Understanding the ripple effects of changes prevents unexpected complications and helps create accurate timelines.

4. **Legacy pattern clustering to identify systematic issues**
   - Necessary for addressing root causes rather than symptoms. Clustering reveals architectural problems that affect multiple components, enabling more efficient wholesale improvements.

5. **Incremental modernization roadmap generation**
   - Required for managing risk and maintaining system stability during updates. A phased approach allows for continuous delivery while systematically eliminating legacy patterns.

## Technical Requirements

- **Testability Requirements**
  - Deprecated API detection must be verifiable with known legacy patterns
  - Technical debt calculations must be reproducible with test data
  - Effort estimation algorithms must be validated against historical data
  - Clustering algorithms must produce consistent results

- **Performance Expectations**
  - Full codebase analysis completes within 30 minutes for 1M LOC
  - Incremental analysis processes changes in under 1 minute
  - Memory usage scales linearly with codebase size
  - Results caching for expensive computations

- **Integration Points**
  - Version control history analysis for pattern age determination
  - Dependency graph construction from imports and references
  - Configuration files for custom deprecation rules
  - Export capabilities for project management tools

- **Key Constraints**
  - Must handle codebases with 10+ years of history
  - Should work with incomplete or missing dependencies
  - Must process mixed Python 2/3 codebases
  - Cannot require modification of analyzed code

**IMPORTANT:** The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The legacy code modernization analyzer must provide:

1. **Deprecation Detection Engine**
   - Comprehensive deprecated API catalog
   - Version-aware deprecation tracking
   - Alternative API suggestions with examples
   - Compatibility matrix generation

2. **Technical Debt Assessment**
   - Multi-factor debt scoring algorithm
   - Maintenance cost estimation based on change frequency
   - Code complexity impact on debt scores
   - Team velocity considerations

3. **Refactoring Analysis System**
   - Dependency graph construction and analysis
   - Change impact propagation modeling
   - Effort estimation based on complexity metrics
   - Risk assessment for proposed changes

4. **Pattern Clustering Engine**
   - Similarity-based legacy pattern grouping
   - Root cause analysis for systematic issues
   - Architectural smell detection
   - Component coupling analysis

5. **Roadmap Generation System**
   - Priority-based modernization scheduling
   - Dependency-aware task ordering
   - Risk-balanced phase planning
   - Progress tracking integration

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of deprecated APIs across Python versions
- Correct technical debt scoring calculations
- Realistic refactoring effort estimations
- Meaningful pattern clustering results
- Actionable roadmap generation

### Critical User Scenarios
- Initial analysis of decade-old legacy codebase
- Identifying highest-priority modernization targets
- Estimating effort for specific refactoring tasks
- Tracking progress through modernization phases
- Re-analyzing after partial modernization

### Performance Benchmarks
- 1M LOC analysis completes within 30 minutes
- Incremental analysis under 1 minute
- Memory usage under 4GB for large codebases
- Roadmap generation within 2 minutes
- Pattern clustering scales to 10,000+ instances

### Edge Cases and Error Conditions
- Handling Python 2/3 mixed codebases
- Processing code with missing dependencies
- Managing circular dependency scenarios
- Dealing with dynamic imports and reflection
- Recovering from version control access issues

### Required Test Coverage Metrics
- Minimum 85% overall code coverage
- 100% coverage for debt scoring algorithms
- All deprecation rules must have test cases
- Clustering algorithms fully tested
- Error recovery paths comprehensively covered

**IMPORTANT:**
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- **REQUIRED:** Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria

The implementation successfully meets the legacy code maintainer's needs when:

1. **Deprecation Coverage**
   - Detects 95%+ of deprecated API usage
   - Provides viable migration paths for each finding
   - Accurately identifies Python version requirements
   - Handles third-party library deprecations

2. **Technical Debt Insights**
   - Debt scores correlate with actual maintenance effort
   - High-debt areas align with team pain points
   - Scoring factors are transparent and adjustable
   - Historical trends are trackable

3. **Refactoring Planning**
   - Effort estimates are within 20% of actual time
   - Dependency impacts are accurately predicted
   - Risk assessments prevent major surprises
   - Plans are actionable and specific

4. **Modernization Progress**
   - Roadmaps lead to measurable improvements
   - Phases can be completed independently
   - Progress tracking shows clear advancement
   - Technical debt decreases over time

**REQUIRED FOR SUCCESS:**
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the development environment:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install project in development mode
uv pip install -e .
```

**REMINDER:** The implementation MUST emphasize that generating and providing pytest_results.json is a critical requirement for project completion.