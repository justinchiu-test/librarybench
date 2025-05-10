# Non-Profit Impact CMS

A specialized content management system designed for environmental organizations to showcase impact, recruit volunteers, and manage campaigns.

## Overview

Non-Profit Impact CMS is a comprehensive content management library tailored for environmental organizations. It enables non-profit coordinators to showcase impact stories, maintain an active event calendar, manage volunteer opportunities, track campaign progress, and distribute newsletters, all while allowing multiple staff members to contribute content with minimal training.

## Persona Description

Jamal coordinates activities for a local environmental organization that needs to inspire community action and recruit volunteers. His primary goal is to showcase impact stories and maintain an active calendar of events while enabling multiple staff members to contribute content with minimal training.

## Key Requirements

1. **Campaign Page Templates with Donation Tracking**: Develop a flexible campaign management system with customizable templates and real-time donation goal tracking. This is critical for Jamal as it visually demonstrates funding progress, creates urgency for potential donors, and helps the organization transparently communicate its financial needs for specific environmental initiatives.

2. **Volunteer Opportunity Database**: Create a comprehensive volunteer management system that organizes opportunities by project, skill requirements, and time commitment with an integrated signup workflow. This feature is essential as volunteer recruitment is core to the organization's ability to execute environmental projects, and structured data helps match volunteers with appropriate opportunities.

3. **Impact Visualization Tools**: Implement data visualization components that convert project outcomes into compelling graphics (charts, maps, infographics data). This functionality is vital for communicating the organization's concrete achievements to stakeholders, turning abstract environmental impact into tangible results that inspire continued support and engagement.

4. **Grant-specific Reporting System**: Develop a flexible reporting framework that can generate customized impact reports based on grant requirements and project metrics. This capability is crucial for maintaining funding relationships, as different grantors have specific reporting requirements that must be met to ensure continued financial support.

5. **Newsletter Template System**: Create a newsletter composition and subscriber management system with templates optimized for environmental content. This feature is important as regular communication helps maintain community engagement, share recent successes, and mobilize supporters for upcoming initiatives and events.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Donation tracking calculations must be thoroughly tested
- Volunteer matching algorithms must be verifiable through test fixtures
- Data visualization outputs must be validated for accuracy
- Newsletter generation must be testable with mock data

### Performance Expectations
- Campaign page rendering must complete within 200ms
- Volunteer opportunity searches should return results within 100ms
- Impact visualization generation should process within 500ms
- Report generation should complete within 3s for complex reports
- Newsletter distribution preparation should handle lists of 10,000+ subscribers

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Payment processor integration hooks for donations
- Calendar export in standard formats (iCal, CSV)
- Export capabilities for volunteer data
- Email service integration for newsletters and notifications

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- Data visualization must be generatable as static images and data

## Core Functionality

The library must provide the following core components:

1. **Campaign Management System**:
   - Campaign definition with goals, timelines, and metrics
   - Donation tracking and goal visualization
   - Campaign status and progress reporting
   - Multiple campaign management
   - Success metrics and outcome recording

2. **Volunteer Management**:
   - Opportunity definition and categorization
   - Skill and interest tagging
   - Time commitment and scheduling
   - Application and approval workflow
   - Volunteer hour tracking and reporting

3. **Impact Reporting System**:
   - Project outcome data modeling
   - Metric definition and calculation
   - Visualization generation (charts, maps, etc.)
   - Comparative analysis tools
   - Before/after demonstration capabilities

4. **Grant Reporting Framework**:
   - Report template definition
   - Custom field configuration
   - Data aggregation from multiple sources
   - Output formatting (PDF, DOC, etc.)
   - Submission tracking and history

5. **Newsletter System**:
   - Template design and management
   - Subscriber list management
   - Content composition and scheduling
   - Engagement tracking data
   - Archive management

6. **Collaborative Content Tools**:
   - Multi-user editing capabilities
   - Content approval workflows
   - Change tracking and history
   - User role management
   - Content assignment system

## Testing Requirements

### Key Functionalities to Verify
- Creation, retrieval, update, and deletion of all content types
- Accurate tracking and visualization of donation progress
- Proper matching of volunteers with appropriate opportunities
- Correct generation of impact visualizations from source data
- Successful creation and delivery of newsletters

### Critical User Scenarios
- Creating and managing a fundraising campaign with real-time goal tracking
- Posting and filling volunteer opportunities across multiple projects
- Generating impact reports for different audiences and purposes
- Creating custom reports for specific grant requirements
- Composing and preparing newsletters for distribution

### Performance Benchmarks
- Campaign page rendering with various levels of donation activity
- Volunteer opportunity search with different filter combinations
- Impact visualization generation with increasingly complex data sets
- Report generation with varying amounts of project data
- Newsletter preparation with different subscriber list sizes

### Edge Cases and Error Conditions
- Handling campaigns that exceed or fall short of funding goals
- Managing volunteer opportunities with specific skill requirements
- Recovering from invalid or inconsistent impact data
- Generating reports when data is incomplete
- Handling newsletter delivery failures

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of donation calculation code
- All error handling paths must be tested
- Performance tests for search and visualization operations
- Security tests for multi-user editing capabilities

## Success Criteria

The implementation will be considered successful when:

1. Campaigns can be created with real-time donation tracking that accurately reflects progress toward goals
2. Volunteers can be effectively matched with opportunities based on skills and availability
3. Impact data can be visually represented in compelling, accurate ways
4. Customized reports can be generated for different grant providers with relevant metrics
5. Newsletters can be created from templates and prepared for distribution to subscriber lists
6. Multiple staff members can contribute content within appropriate permission boundaries
7. All operations can be performed programmatically through a well-documented API
8. The entire system can be thoroughly tested using pytest with high coverage
9. Performance meets or exceeds the specified benchmarks

## Setup and Development

To set up your development environment:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install necessary development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest path/to/test.py::test_function_name
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```

Remember to adhere to the code style guidelines in the project's CLAUDE.md file, including proper type hints, docstrings, and error handling.