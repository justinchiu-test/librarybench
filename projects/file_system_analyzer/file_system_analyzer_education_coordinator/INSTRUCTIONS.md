# Academic Storage Resource Management System

## Overview
A specialized file system analysis library for educational environments that helps efficiently allocate limited storage resources across faculty, research, and student needs. This solution provides quota management, usage pattern analysis, and educational content identification.

## Persona Description
Miguel manages IT resources for a university department with limited budget but diverse computing needs. He needs to efficiently allocate storage resources across faculty, research, and student needs.

## Key Requirements
1. **User quota analysis and recommendation engine**
   - Develop intelligent algorithms for analyzing historical usage patterns by user and group
   - Create predictive models for future storage needs based on user types and activities
   - Generate fair and efficient quota recommendations balancing needs and constraints
   - Track quota utilization and effectiveness over time, with automatic adjustment recommendations

2. **Educational content identification system**
   - Implement classification algorithms to differentiate course materials from personal files
   - Detect and categorize different types of educational content (lectures, assignments, research data, etc.)
   - Identify shared resources versus individual materials
   - Track content lifecycles across academic terms

3. **Semester-based usage pattern visualization**
   - Create data models representing storage demand fluctuations throughout the academic year
   - Track cyclical patterns tied to academic calendar events (term start/end, exam periods, etc.)
   - Predict peak demand periods for resource planning
   - Generate insights for optimizing provisioning during different academic phases

4. **Shared resource optimization framework**
   - Develop analytics to identify opportunities for consolidated storage services
   - Detect redundant content across users and courses
   - Analyze access patterns to determine optimal sharing structures
   - Generate recommendations for resource pooling and sharing policies

5. **Non-technical reporting system**
   - Design simplified data representations for presenting to non-technical department administrators
   - Create clear metrics for storage utilization, allocation efficiency, and cost-effectiveness
   - Generate budget justification reports based on actual usage data
   - Provide comparison analytics against peer departments or institutions

## Technical Requirements
- **Usability**: Must provide clear, actionable insights suitable for administrators with limited technical background
- **Fairness**: Quota and resource allocation recommendations must be equitable and based on objective metrics
- **Flexibility**: Must accommodate diverse needs of different academic departments and user types
- **Efficiency**: Must maximize utility of limited storage resources without sacrificing educational outcomes
- **Privacy**: Must respect academic privacy while still enabling effective resource management

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Quota Management System**
   - Usage pattern analysis algorithms
   - Predictive modeling for storage needs
   - Fairness-based allocation engine
   - Effectiveness tracking and adjustment

2. **Content Classification Engine**
   - Educational material detection
   - Content categorization algorithms
   - Ownership and sharing analysis
   - Academic lifecycle tracking

3. **Temporal Analysis Framework**
   - Academic calendar correlation
   - Cyclical pattern detection
   - Peak demand prediction
   - Seasonal optimization engine

4. **Resource Consolidation System**
   - Redundancy detection algorithms
   - Access pattern analysis
   - Sharing opportunity identification
   - Policy recommendation engine

5. **Administrative Reporting Framework**
   - Simplified data representation models
   - Key performance indicator tracking
   - Budget justification generators
   - Comparative analysis tools

## Testing Requirements
- **Quota Analysis Testing**
  - Test with simulated usage patterns for various academic user types
  - Validate prediction accuracy with historical data
  - Verify recommendation fairness with controlled allocation scenarios
  - Test adjustment algorithms with changing usage patterns

- **Content Classification Testing**
  - Test with diverse collection of academic and personal files
  - Validate categorization accuracy with pre-classified content
  - Verify lifecycle tracking across simulated academic terms
  - Test with mixed-use content and edge cases

- **Pattern Analysis Testing**
  - Test detection algorithms with academic calendar-aligned data
  - Validate prediction accuracy for peak demand periods
  - Verify optimization recommendations against expert strategies
  - Test with various institutional calendar patterns

- **Resource Optimization Testing**
  - Test redundancy detection with known duplicative content
  - Validate sharing recommendations against best practices
  - Verify access pattern analysis with simulated usage data
  - Test policy recommendations with diverse department structures

- **Reporting Testing**
  - Test clarity and comprehensibility with non-technical reviewers
  - Validate metric accuracy against raw data
  - Verify budget justification quality against institutional standards
  - Test comparative analysis with benchmark datasets

## Success Criteria
1. Generate quota recommendations that accommodate at least 95% of legitimate user needs while staying within overall storage constraints
2. Correctly identify and classify educational content with at least 90% accuracy
3. Predict semester-based usage patterns and peak demands with 85%+ accuracy
4. Identify resource consolidation opportunities that reduce overall storage requirements by at least 25%
5. Create reports that effectively communicate technical storage metrics to non-technical administrators
6. Achieve 90%+ user satisfaction with storage allocation while maintaining strict budget discipline

To set up your development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```