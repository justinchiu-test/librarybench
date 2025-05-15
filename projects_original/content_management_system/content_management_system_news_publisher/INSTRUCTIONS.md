# Local News Content Management System

## Overview
A specialized content management system designed for small-town news services to manage time-sensitive news content, organize articles by category, and generate revenue through local business advertisements. This system enables news publishers to quickly publish content while maintaining organizational control over the editorial process.

## Persona Description
Aisha runs a small town news service covering local events, government, and community stories. Her primary goal is to quickly publish time-sensitive news content while organizing articles by category and importance, and generating revenue through local business advertisements.

## Key Requirements

1. **Breaking news alert system with front page takeover option**
   - Critical for Aisha to rapidly publish urgent news without delay or technical barriers
   - Must include special formatting and prominence controls for high-priority stories
   - Should support push notifications and emergency display options that override normal layouts

2. **Editorial workflow with draft, review, and publishing stages**
   - Essential for maintaining journalistic quality while enabling collaboration among staff writers
   - Must track article status through the editorial process with role-appropriate access
   - Should include revision tracking, editorial comments, and approval workflows

3. **Local ad management system with performance tracking**
   - Important for generating revenue while providing value to local business advertisers
   - Must support various ad formats, placement options, and scheduling
   - Should include impression/click tracking and basic performance analytics

4. **Citizen journalism submission portal with verification tools**
   - Valuable for expanding coverage through community contributions while maintaining editorial standards
   - Must include submission forms, content validation, and fact-checking workflow
   - Should support identity verification and contributor management

5. **Content archiving with advanced search and tagging**
   - Necessary for maintaining a valuable historical record and enabling research in past stories
   - Must organize content chronologically, by topic, and by other relevant attributes
   - Should support complex search queries and contextual content relationships

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% code coverage
- Integration tests must verify the editorial workflow functions correctly
- Performance tests must ensure breaking news publishing meets time requirements
- Mock ad delivery for testing impression and click tracking

### Performance Expectations
- Breaking news publishing must complete within 30 seconds from submission to live
- Article searches must return results within 500ms regardless of archive size
- Ad delivery decision must take less than 100ms per page view
- System must support at least 50 concurrent content editors

### Integration Points
- Email/SMS gateway for breaking news alerts
- Social media platforms for automated sharing
- Payment processing for advertiser billing
- Analytics systems for content and ad performance

### Key Constraints
- Content must be stored in a format suitable for multiple delivery channels
- System must maintain strict content ownership and attribution
- Ad content must be clearly distinguished from editorial content
- Search system must handle complex queries with acceptable performance

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide a Python library with the following core components:

1. **News Article Management**
   - Content data model with metadata and categorization
   - Publishing workflow and status tracking
   - Priority classification and promotion
   - Version control and revision history

2. **Breaking News System**
   - Expedited publishing workflow
   - Alert generation and distribution
   - Front page takeover mechanisms
   - Urgent content formatting and presentation

3. **Editorial Process**
   - Draft management and revision tracking
   - Review assignment and feedback collection
   - Approval workflows and publishing authorization
   - Editorial calendar and scheduling

4. **Advertising Infrastructure**
   - Ad inventory management
   - Placement and targeting rules
   - Impression/click tracking
   - Performance reporting and analytics

5. **Community Contribution**
   - Submission validation and processing
   - Contributor identity verification
   - Fact-checking workflow
   - Content moderation and feedback

6. **Archive and Search**
   - Content indexing and categorization
   - Full-text search with relevance ranking
   - Tagging and metadata management
   - Historical content relationships

## Testing Requirements

### Key Functionalities to Verify
- Breaking news is published rapidly with proper prominence
- Editorial workflow correctly tracks content through all stages
- Ad system delivers appropriate advertisements with accurate tracking
- Community submissions are properly validated and processed
- Archive search returns relevant results based on various criteria

### Critical User Scenarios
- Publishing a breaking news story with alerts and front page takeover
- Managing an article through the complete editorial workflow
- Setting up and monitoring a new advertising campaign
- Processing and verifying a community-submitted news tip
- Researching historical articles on a specific topic or event

### Performance Benchmarks
- Breaking news publishing must complete end-to-end in under 30 seconds
- System must support an archive of at least 100,000 articles
- Search must return results in under 500ms for complex queries
- Ad system must handle at least 100,000 impressions per day

### Edge Cases and Error Conditions
- Handling concurrent edits to the same article
- Managing incomplete or embargoed content
- Dealing with ad delivery failures
- Processing potentially inappropriate community submissions
- Recovering from interrupted publishing operations

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of breaking news publishing logic
- 100% coverage of editorial approval workflows
- 100% coverage of ad delivery and tracking

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

1. The breaking news system enables rapid publishing with appropriate prominence
2. The editorial workflow effectively manages content through all stages
3. The ad system correctly delivers and tracks advertisements
4. The community submission system properly validates and processes contributions
5. The archive and search system effectively organizes and retrieves historical content

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```