# Developer Portfolio Generator

A specialized static site generator for software professionals to create comprehensive, interactive portfolios showcasing their technical skills, projects, and professional experience.

## Overview

This project is a Python library for generating developer portfolio websites from structured data sources. It focuses on GitHub integration, skills visualization, professional experience presentation, and interactive code demonstrations to help software developers effectively showcase their capabilities to potential employers and clients.

## Persona Description

Hiroshi is a software developer who wants to create a professional portfolio site showcasing his skills, projects, and career journey. He needs a developer-friendly way to maintain his professional presence online.

## Key Requirements

1. **GitHub Project Synchronization**: Implement a system to automatically import and feature repositories with proper descriptions and metadata. This integration is critical for Hiroshi to maintain a portfolio that accurately reflects his current work without manual updates, allowing him to showcase code projects directly from his GitHub profile with appropriate context and highlights.

2. **Skills Visualization Framework**: Create a system for visually representing technical expertise with categorization and proficiency levels. As a developer, Hiroshi needs to clearly communicate his technical stack to potential employers, making this feature essential for organizing his diverse skills into meaningful categories (languages, frameworks, tools) with appropriate proficiency indicators.

3. **Work History Timeline**: Develop an interactive timeline displaying professional experience with company information and key accomplishments. This chronological representation helps Hiroshi demonstrate his career progression, highlight notable achievements at each position, and provide context about the companies and projects he has worked with throughout his professional journey.

4. **Interactive Code Demonstration**: Implement functionality for embedding runnable code examples showing programming capabilities in various languages. This feature allows Hiroshi to go beyond listing skills by actually demonstrating his coding style, problem-solving approach, and technical capabilities through interactive examples that visitors can examine and execute directly in the browser.

5. **Professional Endorsement System**: Create a framework for displaying recommendations and endorsements from colleagues and clients. Social proof is valuable in professional contexts, making this feature important for Hiroshi to strengthen his credibility through testimonials from peers, supervisors, and clients who can speak to his technical abilities, collaboration skills, and project outcomes.

## Technical Requirements

- **Testability Requirements**:
  - GitHub synchronization must function with mock API responses
  - Skills visualization must render consistently with different data structures
  - Work history timeline must handle various career paths and formats
  - Code demonstrations must execute in isolated environments
  - Endorsement display must maintain consistent formatting across different lengths

- **Performance Expectations**:
  - Full portfolio generation must complete in under 20 seconds
  - GitHub data fetching should use efficient caching to minimize API calls
  - Code examples should load and execute in under 3 seconds
  - Interactive elements should respond to user input in under 100ms
  - Generated site should score 90+ on Google PageSpeed Insights

- **Integration Points**:
  - GitHub API for repository data
  - Code execution environments (like Pyodide, CodeMirror)
  - Resume data formats (JSON Resume standard)
  - Visualization libraries for skills representation
  - Social media profiles for professional presence linking

- **Key Constraints**:
  - All functionality must work without server-side processing
  - GitHub API rate limits must be respected with proper caching
  - Interactive code execution must be secure and sandboxed
  - Generated site must be deployable to basic static hosting
  - Solution must accommodate ongoing portfolio updates with minimal effort

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality must include:

1. **GitHub Integration System**:
   - Fetch repository data from GitHub API with proper authentication
   - Extract and process repository metadata (languages, stars, description)
   - Generate featured project showcases from selected repositories
   - Create project cards with appropriate details and links
   - Support custom highlighting of specific contributions or features

2. **Skills Management Framework**:
   - Process structured skills data with categories and proficiency levels
   - Generate visual representations of skill groupings
   - Create appropriate indicators for experience or expertise levels
   - Support skill tagging and filtering
   - Link skills to relevant projects and work experiences

3. **Professional History System**:
   - Process structured work and education history data
   - Generate chronological timeline of professional experience
   - Create detailed role descriptions with accomplishments
   - Support company information and context
   - Handle concurrent positions and non-traditional career paths

4. **Code Demonstration Platform**:
   - Process code snippets in various languages with descriptions
   - Create interactive code editors with appropriate syntax highlighting
   - Support execution environments for runnable examples
   - Handle input/output for interactive demonstrations
   - Support multiple code samples grouped by language or concept

5. **Endorsement Management System**:
   - Process structured recommendation data with attribution
   - Generate properly formatted testimonial displays
   - Support categorization of endorsements by type or relationship
   - Verify endorsement authenticity through links or references
   - Create highlight reels of key endorsement quotes

## Testing Requirements

- **Key Functionalities to Verify**:
  - Accurate fetching and displaying of GitHub repository information
  - Correct visualization of skills with appropriate categorization
  - Proper rendering of career timeline with all experience details
  - Functional execution of code examples with expected outputs
  - Consistent display of professional endorsements

- **Critical User Scenarios**:
  - Portfolio owner adds a new GitHub project that appears in their portfolio
  - Visitor explores skills visualization to understand technical expertise
  - Recruiter reviews professional history to assess career progression
  - Technical evaluator runs code examples to assess coding style
  - Potential client reviews endorsements to gauge professional reputation

- **Performance Benchmarks**:
  - GitHub synchronization time with various repository counts
  - Skills visualization rendering performance with different skill sets
  - Timeline generation time with varying career lengths
  - Code example load and execution time across different languages
  - Overall build time for portfolios of different complexity

- **Edge Cases and Error Conditions**:
  - Handling of GitHub API rate limiting or temporary failures
  - Management of overlapping or concurrent job positions
  - Processing of code examples with execution errors
  - Handling of very long or detailed endorsements
  - Recovery from incomplete or malformed input data

- **Required Test Coverage**:
  - 90% code coverage for GitHub integration components
  - 90% coverage for skills visualization system
  - 85% coverage for timeline generation
  - 95% coverage for code demonstration functionality
  - 85% coverage for endorsement management

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. GitHub projects are automatically synchronized and properly featured in the portfolio
2. Technical skills are clearly visualized with appropriate categorization and levels
3. Professional experience is presented in a comprehensive, chronological timeline
4. Code examples execute correctly in the browser with appropriate context
5. Professional endorsements are displayed with proper attribution and formatting
6. The portfolio automatically updates when source data changes
7. All tests pass with at least 90% code coverage
8. The generated site is fast, responsive, and scores well on web performance metrics

To set up your development environment:
```
uv venv
source .venv/bin/activate
```