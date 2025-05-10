# Local News CMS

A specialized content management system designed for local news organizations to quickly publish time-sensitive content and manage community stories.

## Overview

Local News CMS is a comprehensive content management library tailored for small-town news services. It enables publishers to quickly publish time-sensitive news, organize articles by category and importance, manage local business advertisements, facilitate citizen journalism, and maintain searchable archives, all while maintaining editorial quality and community relevance.

## Persona Description

Aisha runs a small town news service covering local events, government, and community stories. Her primary goal is to quickly publish time-sensitive news content while organizing articles by category and importance, and generating revenue through local business advertisements.

## Key Requirements

1. **Breaking News Alert System**: Develop a priority-based publishing system with front page takeover capability for urgent stories. This is critical for Aisha as it allows her news service to immediately inform the community about emergencies, severe weather, important civic announcements, and other time-sensitive news that affects public safety and community wellbeing.

2. **Editorial Workflow Management**: Create a comprehensive content workflow system with draft, review, and publishing stages for collaborative news production. This feature is essential as it enables Aisha to maintain journalistic standards by implementing proper editorial oversight, fact-checking, and quality control while still allowing multiple contributors to efficiently produce content.

3. **Local Advertisement Management**: Implement a flexible advertising system that handles placement, scheduling, and performance tracking for local business ads. This functionality is vital for the financial sustainability of Aisha's news service, providing a reliable revenue stream through targeted local business advertising while delivering measurable value to advertisers.

4. **Citizen Journalism Portal**: Develop a submission and verification framework for community-contributed content with editorial review tools. This capability is important for expanding coverage of hyperlocal events and diverse perspectives, allowing the news service to maintain community engagement and cover more stories than would be possible with staff reporters alone.

5. **Content Archiving and Search**: Create a robust archiving system with advanced search, tagging, and categorization for retrieving historical content. This feature is crucial for building a valuable community resource of local history and allowing readers to research past events, providing context for current stories and increasing the long-term value of the news service.

## Technical Requirements

### Testability Requirements
- All components must have unit tests with at least 90% coverage
- Publishing workflow must be thoroughly tested with various scenarios
- Ad placement algorithms must be verifiable through test fixtures
- Search functionality must be validated with comprehensive test cases
- Performance must be tested under various load conditions

### Performance Expectations
- Breaking news publishing must complete within 5 seconds end-to-end
- Article searches should return results within 200ms
- Ad rendering and placement must process within 100ms
- The system should handle at least 50 concurrent edit sessions
- Archive searches should efficiently handle 10+ years of content

### Integration Points
- Support for common storage backends (local filesystem, SQLite, optional cloud storage)
- Email notification system for editorial alerts
- Analytics integration for readership and ad performance
- Social media publishing hooks
- RSS feed generation

### Key Constraints
- All code must be pure Python with minimal dependencies
- No JavaScript dependencies or browser-specific code
- No direct coupling to web frameworks, though adaptors can be provided
- All content must be serializable for backup/restore
- System must operate reliably on limited hardware resources

## Core Functionality

The library must provide the following core components:

1. **News Publishing System**:
   - Article creation and formatting
   - Category and tag management
   - Priority-based presentation rules
   - Breaking news flagging
   - Publishing scheduling

2. **Editorial Workflow**:
   - Multi-stage content approval process
   - Role-based editing permissions
   - Revision tracking and comparison
   - Editorial comments and feedback
   - Quality control checklists

3. **Advertising Framework**:
   - Ad placement and positioning rules
   - Scheduling and rotation
   - Performance tracking and analytics
   - Advertiser account management
   - Campaign reporting

4. **Community Contribution System**:
   - Submission forms and guidelines
   - Content verification workflow
   - Contributor recognition
   - Moderation tools and policies
   - Community feedback mechanisms

5. **Archive and Search System**:
   - Content indexing and categorization
   - Full-text search capabilities
   - Date-based and topic-based browsing
   - Related content suggestions
   - Historical context linking

6. **Analytics and Reporting**:
   - Readership tracking and analysis
   - Content performance metrics
   - Ad engagement measurement
   - Editorial workflow efficiency
   - Trend identification and reporting

## Testing Requirements

### Key Functionalities to Verify
- Creation, editing, review, and publishing of news articles
- Proper triggering and display of breaking news alerts
- Accurate placement and tracking of advertisements
- Successful submission and moderation of citizen-contributed content
- Effective indexing and searching of archived content

### Critical User Scenarios
- Publishing breaking news with front page prominence
- Moving an article through the complete editorial workflow
- Setting up and monitoring a local business advertising campaign
- Processing and publishing community-submitted news tips
- Researching and retrieving historical articles on a specific topic

### Performance Benchmarks
- Breaking news publishing time from creation to front page
- Search response time with growing content archive
- Ad placement calculation with multiple targeting rules
- System behavior with concurrent editing sessions
- Archive retrieval speed for articles of different ages

### Edge Cases and Error Conditions
- Handling multiple simultaneous breaking news events
- Managing editorial workflow conflicts
- Recovering from interrupted publishing processes
- Behavior when search indexes need rebuilding
- Handling malformed or inappropriate community submissions

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core components
- 100% coverage of publishing workflow code
- All error handling paths must be tested
- Performance tests for search and publishing operations
- Security tests for community submission processing

## Success Criteria

The implementation will be considered successful when:

1. Breaking news can be published and prominently displayed within seconds of creation
2. The editorial workflow ensures quality content while maintaining publishing efficiency
3. Local businesses can effectively advertise with placement options and performance tracking
4. Community members can submit content that is properly vetted and integrated
5. Years of content can be archived and easily searched by readers and staff
6. All operations can be performed programmatically through a well-documented API
7. The entire system can be thoroughly tested using pytest with high coverage
8. Performance meets or exceeds the specified benchmarks

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