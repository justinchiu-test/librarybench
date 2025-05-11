# Academic Storage Resource Manager

A specialized file system analyzer for educational environments focused on optimizing storage allocation among faculty, research, and student needs.

## Overview

The Academic Storage Resource Manager is a Python library designed to help educational IT coordinators efficiently allocate limited storage resources across diverse computing needs in academic environments. It provides tools for user quota analysis, educational content identification, semester-based usage pattern visualization, shared resource optimization, and simplified reporting for non-technical stakeholders.

## Persona Description

Miguel manages IT resources for a university department with limited budget but diverse computing needs. He needs to efficiently allocate storage resources across faculty, research, and student needs.

## Key Requirements

1. **User Quota Analysis and Recommendation Engine**:
   Tools to analyze historical usage patterns and recommend appropriate quota allocations for different user groups. This is critical for Miguel because it enables data-driven decisions about storage allocation rather than arbitrary assignments. The system must analyze usage trends over time to identify both underutilized and constrained allocations, then suggest optimal quota adjustments.

2. **Educational Content Identification**:
   Mechanisms to automatically distinguish course materials from personal files and research data. This feature is essential because it allows Miguel to implement appropriate retention and backup policies for different content types. Academic files have different lifecycle and protection requirements than personal files, and Miguel needs to ensure critical educational resources are properly preserved.

3. **Semester-Based Usage Pattern Visualization**:
   Analytics that visualize storage demand fluctuations throughout the academic year. This capability is crucial for capacity planning as academic environments experience predictable usage spikes aligned with the semester calendar. Miguel needs to understand these patterns to prepare infrastructure for peak demand periods like finals and project deadlines.

4. **Shared Resource Optimization**:
   Tools to identify opportunities for consolidating storage services and eliminating redundancy. This is vital in budget-constrained educational environments where efficiency is paramount. Miguel needs to identify duplicate content, underutilized personal storage, and opportunities for shared storage pools to maximize resource efficiency.

5. **Simplified Reporting for Non-Technical Stakeholders**:
   Generation of clear, graphical reports designed for presentation to department administrators without technical backgrounds. This feature is essential because Miguel must justify IT resource allocations to administrative leadership. Reports must translate technical metrics into business-relevant insights that demonstrate efficient resource utilization and support budget requests.

## Technical Requirements

### Testability Requirements
- All components must have clear APIs that can be tested independently
- Test fixtures should include sample educational directory structures
- Quota analysis algorithms must be testable with historical usage datasets
- Report generation must be verifiable through automated testing
- Test suites should achieve at least 90% code coverage

### Performance Expectations
- User quota analysis should complete in under 5 minutes for departments with 1,000+ users
- Content classification should process at least 100GB per hour
- Memory usage should not exceed 500MB during standard operations
- Analysis results should be cached with efficient incremental updates
- Operations should have minimal impact on active file systems

### Integration Points
- Standard filesystem access interfaces (local and network storage)
- User directory service integration (LDAP, Active Directory)
- Course management system integration (optional)
- Export capabilities for reports (PDF, HTML, Excel)
- Email notification systems for quota alerts

### Key Constraints
- All operations must be read-only to avoid disrupting educational activities
- Privacy regulations for student data must be strictly observed
- Implementation must support heterogeneous environments (Windows, Mac, Linux)
- Solutions must be implementable with limited IT staff resources
- Analysis must work across both centralized and distributed storage systems

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Academic Storage Resource Manager must provide the following core functionality:

1. **User Storage Analysis Framework**:
   - Historical usage tracking by user and group
   - Trend analysis for growth prediction
   - Anomaly detection for unusual storage consumption
   - Comparative analysis between similar user groups
   - Quota recommendation algorithms with configurable parameters

2. **Content Classification System**:
   - Pattern-based identification of educational materials
   - Course-related file detection and organization
   - Differentiation between research, educational, and personal content
   - File lifecycle stage determination
   - Content ownership and sharing analysis

3. **Temporal Usage Analysis**:
   - Academic calendar correlation with storage patterns
   - Detection of cyclical usage trends
   - Peak demand period identification
   - Predictive modeling for future semesters
   - Historical comparison across academic years

4. **Resource Consolidation Engine**:
   - Duplicate content detection across user directories
   - Shared storage opportunity identification
   - Cold data archival recommendation
   - Multi-user access pattern analysis
   - Resource pooling strategy suggestions

5. **Stakeholder Reporting System**:
   - Automated report generation with configurable templates
   - Visual representation of key storage metrics
   - Cost analysis and budget justification tools
   - Comparison with peer institutions (if data available)
   - Executive summaries for administrative leadership

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of quota recommendations based on historical data
- Precision of educational content identification
- Reliability of semester-based usage pattern detection
- Effectiveness of shared resource optimization recommendations
- Clarity and correctness of generated reports

### Critical User Scenarios
- Start-of-semester storage provisioning for new courses
- End-of-semester cleanup and archival operations
- Mid-year budget justification reporting
- Storage reallocation between departments
- Handling of special projects with temporary storage needs

### Performance Benchmarks
- Complete analysis of a department with 1,000 users in under 10 minutes
- Processing of 1TB educational file system in under 1 hour
- Memory usage below 500MB during all operations
- Report generation in under 30 seconds
- API response times under 200ms for standard queries

### Edge Cases and Error Conditions
- Handling of permission restrictions in mixed-access environments
- Graceful operation with incomplete historical data
- Proper analysis of unusual file types specific to academic disciplines
- Recovery from interrupted scans
- Appropriate handling of very large individual directories (e.g., research data)

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of report generation functions
- All recommendation algorithms must have dedicated test suites
- Performance tests for resource-intensive operations
- Integration tests for all supported storage systems

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

The Academic Storage Resource Manager implementation will be considered successful when:

1. Quota recommendations accurately reflect actual needs based on historical patterns
2. Content classification correctly identifies at least 90% of educational materials
3. Semester-based usage visualizations clearly show academic calendar correlations
4. Shared resource recommendations identify significant consolidation opportunities
5. Generated reports effectively communicate technical information to non-technical stakeholders
6. Implementation meets all performance benchmarks
7. Code is well-structured, maintainable, and follows Python best practices
8. The system can be deployed in varied educational environments with minimal configuration

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

NOTE: To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion. Use the following commands:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```