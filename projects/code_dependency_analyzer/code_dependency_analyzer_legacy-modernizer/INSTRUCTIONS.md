# Legacy System Modernization Analyzer

## Overview
A specialized dependency analysis tool designed for consultants modernizing legacy codebases, helping them understand tangled dependencies, plan incremental modernization strategies, and safely extract modules without breaking existing functionality.

## Persona Description
A software consultant specializing in modernizing legacy codebases. They need to understand tangled dependencies to plan incremental modernization strategies.

## Key Requirements
1. **Legacy pattern identification in dependency structures**: The tool must recognize common legacy patterns (god classes, spaghetti dependencies, outdated architectural styles) and categorize them by modernization difficulty and risk.

2. **Strangler fig pattern application planning**: Critical for safe modernization, the system must analyze dependencies to identify optimal boundaries for strangler fig implementation, suggesting which components can be safely isolated and replaced incrementally.

3. **Module extraction feasibility analysis**: Essential for refactoring, the tool must assess how easily modules can be extracted from the legacy system, calculating the effort required to decouple dependencies and maintain backward compatibility.

4. **Database coupling detection through shared imports**: To prevent data consistency issues, the system must identify when multiple modules access the same database tables or ORM models, highlighting shared data dependencies that complicate modernization.

5. **Modernization roadmap generation with milestones**: For project planning, the tool must generate step-by-step modernization roadmaps with clear milestones, dependency-based ordering, and risk assessments for each phase.

## Technical Requirements
- **Testability requirements**: All pattern detection algorithms must be unit testable with sample legacy code structures. Integration tests should verify roadmap generation against known modernization scenarios.
- **Performance expectations**: Must analyze legacy codebases with 500,000+ lines within 30 minutes. Pattern detection should work incrementally to support iterative analysis.
- **Integration points**: Must integrate with version control for historical analysis, database schema tools for data coupling detection, and project management systems for roadmap export.
- **Key constraints**: Must handle obsolete Python versions, work with incomplete or corrupted codebases, and provide meaningful analysis even with missing dependencies.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must detect legacy anti-patterns in dependency structures, assess module extraction feasibility with effort estimates, identify database coupling through import analysis, plan strangler fig boundaries based on dependencies, and generate phased modernization roadmaps. The system should support custom pattern definitions and provide APIs for modernization tracking.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate legacy pattern detection and classification
  - Correct strangler fig boundary recommendations
  - Valid module extraction feasibility scores
  - Proper database coupling identification
  - Realistic modernization roadmap generation

- **Critical user scenarios that should be tested**:
  - Analyzing a 20-year-old monolithic ERP system
  - Planning strangler fig for a legacy e-commerce platform
  - Extracting authentication from a tightly coupled system
  - Identifying shared database dependencies in a multi-tenant app
  - Creating a 2-year modernization roadmap for a financial system

- **Performance benchmarks that must be met**:
  - Analyze 100,000 lines of legacy code in under 10 minutes
  - Generate extraction plans for 50 modules in under 5 minutes
  - Detect database coupling in 1,000 files in under 2 minutes
  - Create modernization roadmaps in under 60 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Python 2.x codebases requiring migration
  - Mixed language systems with Python components
  - Circular dependencies preventing extraction
  - Missing source files referenced in imports
  - Database access through raw SQL strings

- **Required test coverage metrics**:
  - Minimum 90% code coverage for pattern detection
  - 100% coverage for roadmap generation logic
  - Full coverage of feasibility analysis algorithms
  - Integration tests for various legacy scenarios

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
Clear metrics and outcomes that would indicate the implementation successfully meets this persona's needs:
- Identifies 90% of modernization blockers in legacy systems
- Generates roadmaps that reduce modernization risk by 70%
- Accurately estimates extraction effort within 20% of actual time
- Enables incremental modernization without breaking production
- Reduces modernization project duration by 40% through better planning

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
From within the project directory, set up the development environment:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```