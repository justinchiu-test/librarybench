# Developer Portfolio Site Generator

A specialized static site generator designed for software developers to create professional portfolio websites showcasing their technical skills, projects, work history, and code demonstrations.

## Overview

This project implements a Python library for generating developer portfolio websites that highlight technical projects, skills, and professional experience. It focuses on the needs of software developers who want a developer-friendly way to maintain their professional online presence with features specifically tailored to showcase coding capabilities and career achievements.

## Persona Description

Hiroshi is a software developer who wants to create a professional portfolio site showcasing his skills, projects, and career journey. He needs a developer-friendly way to maintain his professional presence online.

## Key Requirements

1. **GitHub Project Synchronization**: Implement direct integration with GitHub to automatically feature repositories with proper descriptions, languages, and contribution statistics.
   - Critical for Hiroshi because his GitHub projects represent his best work, and automatic synchronization ensures his portfolio stays current without manual updates when he publishes new code.
   - Must pull repository details, README content, stars, forks, and other relevant metrics.

2. **Skills Visualization**: Create a system for showcasing technical expertise with categorization and proficiency levels using visual representations.
   - Essential for Hiroshi because potential employers need to quickly understand his technical capabilities and specialization areas, with visual elements making this information more digestible.
   - Should organize skills by category (languages, frameworks, tools) with customizable visualization options.

3. **Work History Timeline**: Develop a professional experience timeline with company information, role descriptions, technologies used, and key accomplishments.
   - Important for Hiroshi because his career progression and professional achievements are central to his value proposition, and a timeline format clearly shows growth and experience.
   - Must present experience in a chronological, visually appealing format with detailed role information.

4. **Interactive Code Demonstrations**: Implement embeddable, interactive code samples that showcase programming capabilities in various languages with execution capabilities.
   - Valuable for Hiroshi because actual code demonstrations prove his abilities far better than just listing skills, and interactivity allows visitors to explore his coding style.
   - Should support syntax highlighting, execution, and customization for multiple programming languages.

5. **Professional Endorsement Display**: Create a system for featuring recommendations and endorsements from colleagues and clients with proper attribution.
   - Critical for Hiroshi because third-party validation adds credibility to his claimed expertise, and professional connections are an important aspect of his professional profile.
   - Should include testimonial formatting with endorser information and relationship context.

## Technical Requirements

### Testability Requirements
- All components must be individually testable with clear interfaces
- Mock GitHub API responses for testing repository integration
- Support snapshot testing for generated portfolio sections
- Test code demonstration execution in various languages
- Validate skills visualization with comprehensive test datasets

### Performance Expectations
- GitHub repository synchronization should process 20+ repositories efficiently
- Skills visualization should render quickly even with 50+ technical skills
- Timeline generation should handle full career history in under 3 seconds
- Code demonstrations should initialize in under 500ms
- Full portfolio site generation should complete in under 20 seconds

### Integration Points
- GitHub API for repository data extraction
- Code execution environments for interactive demonstrations
- Visualization libraries for skills representation
- Responsive image handling for work history and endorsements
- Social profile linking and integration

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- Must handle GitHub API rate limiting gracefully
- Interactive code demonstrations must be secure and sandboxed
- Generated portfolio must be optimized for technical recruiters and hiring managers
- Output must be fully responsive for viewing on various devices
- Must provide proper caching for GitHub data to minimize API calls

## Core Functionality

The Developer Portfolio Site Generator should provide a comprehensive Python library with the following core capabilities:

1. **GitHub Integration System**
   - Connect to GitHub API using authentication tokens
   - Extract repository details, languages, and statistics
   - Process README files for project descriptions
   - Filter and categorize repositories by topics/languages
   - Generate project showcases with appropriate metrics
   - Implement caching to respect API rate limits

2. **Skills Management**
   - Process skill data with categorization and proficiency
   - Generate visual representations of skill sets
   - Implement grouping by technology categories
   - Create comparative visualizations for skill emphasis
   - Support for skill endorsement integration
   - Generate skill-based project filtering

3. **Career Timeline Generator**
   - Process work history with company and role details
   - Generate chronological timeline visualizations
   - Implement role description formatting
   - Create project and accomplishment highlighting
   - Support for education and certification inclusion
   - Generate printable resume versions

4. **Code Demonstration Engine**
   - Process code samples in various languages
   - Generate interactive code environments
   - Implement syntax highlighting and formatting
   - Create execution contexts for running examples
   - Support for example input/output demonstration
   - Generate embeddable code widgets

5. **Endorsement Management**
   - Process testimonial and endorsement data
   - Generate formatted testimonial displays
   - Implement attribution and relationship context
   - Create endorsement categorization by skill area
   - Support for verification and linking
   - Generate social proof highlighting

## Testing Requirements

### Key Functionalities to Verify

1. **GitHub Repository Integration**
   - Test GitHub API connection and authentication
   - Verify repository data extraction and formatting
   - Test readme processing and rendering
   - Confirm proper handling of repository statistics
   - Verify caching mechanisms and rate limit handling
   - Test repository filtering and categorization

2. **Skills Visualization**
   - Test skill data processing with various formats
   - Verify visualization generation for different skill sets
   - Test categorization and grouping functionality
   - Confirm proper representation of proficiency levels
   - Verify responsive behavior of skill visualizations
   - Test skill filtering and sorting

3. **Work History Timeline**
   - Test timeline generation with various career paths
   - Verify proper chronological ordering and formatting
   - Test company and role information extraction
   - Confirm inclusion of accomplishments and technologies
   - Verify education and certification integration
   - Test printable format generation

4. **Code Demonstration**
   - Test code snippet processing in multiple languages
   - Verify syntax highlighting accuracy
   - Test execution environment setup and isolation
   - Confirm proper output display and formatting
   - Verify language-specific features
   - Test interactive elements and user modifications

5. **Endorsement System**
   - Test testimonial formatting and attribution
   - Verify proper relationship context display
   - Test endorsement categorization by skill
   - Confirm randomization or prioritization features
   - Verify linking to endorser profiles
   - Test endorsement filtering and highlighting

### Critical User Scenarios

1. Synchronizing GitHub repositories and seeing them properly showcased on the portfolio
2. Creating a comprehensive skills visualization that accurately represents technical capabilities
3. Building a career timeline that highlights professional growth and accomplishments
4. Embedding interactive code samples that demonstrate programming expertise
5. Featuring professional endorsements that build credibility and provide social proof

### Performance Benchmarks

- GitHub synchronization should complete in under 10 seconds for 20+ repositories
- Skills visualization should render in under 1 second even with 50+ skills
- Timeline generation should process a 10+ year career history in under 3 seconds
- Code demonstration environments should load in under 500ms
- Full portfolio generation should complete in under 20 seconds

### Edge Cases and Error Conditions

- Test handling of GitHub API failures or rate limiting
- Verify behavior with repositories containing unusual languages
- Test with extremely long work histories or numerous positions
- Verify code execution with edge cases and potential errors
- Test with missing data for certain portfolio sections
- Validate behavior with unusually large code samples
- Test with international/non-English content

### Required Test Coverage Metrics

- Minimum 90% code coverage for core functionality
- 100% coverage for GitHub integration logic
- 100% coverage for code demonstration features
- Integration tests for the entire portfolio generation pipeline
- Performance tests for both small and comprehensive portfolios

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

The Developer Portfolio Site Generator will be considered successful if it:

1. Successfully synchronizes with GitHub repositories to showcase projects with appropriate details
2. Creates visually appealing skills representations with proper categorization and proficiency levels
3. Generates a comprehensive work history timeline highlighting career progression
4. Provides functional, interactive code demonstrations in various programming languages
5. Presents professional endorsements with proper attribution and context
6. Builds portfolio sites efficiently with proper organization and hierarchy
7. Produces responsive, performance-optimized HTML output
8. Facilitates easy updates when new projects or skills are added

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up your development environment:

1. Create a virtual environment using UV:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: When testing, you must generate the pytest_results.json file:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

This file is MANDATORY proof that all tests pass and must be included with your implementation.