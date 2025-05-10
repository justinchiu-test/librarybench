# Developer Portfolio Site Generator

A specialized static site generator optimized for software developers to create professional portfolio websites showcasing their skills, projects, and career journey.

## Overview

This project provides a developer-focused static site generator that enables software professionals to create, maintain, and update a portfolio website showcasing their skills, projects, and career journey. The system automates the generation of technical content such as project showcases, skills visualization, and code demonstrations.

## Persona Description

Hiroshi is a software developer who wants to create a professional portfolio site showcasing his skills, projects, and career journey. He needs a developer-friendly way to maintain his professional presence online.

## Key Requirements

1. **GitHub Project Synchronization**: Automatically feature repositories with proper descriptions.
   - As a developer, Hiroshi's code repositories are his most important work samples, so automatic synchronization with GitHub ensures his portfolio always reflects his latest projects.
   - This feature must fetch repository data, readme content, languages used, stars, forks, and other metrics, presenting them in a visually appealing and informative manner.

2. **Skills Visualization**: Present technical expertise with categorization and proficiency levels.
   - Communicating technical skills effectively is essential for job opportunities, so Hiroshi needs a system to showcase his abilities with proper categorization and experience levels.
   - The system should generate visual representations of skills grouped by category (languages, frameworks, tools, etc.) with indicators of proficiency and experience duration.

3. **Work History Timeline**: Display career progression with company information and accomplishments.
   - Presenting professional growth and experience is crucial for establishing credibility, requiring a chronological presentation of Hiroshi's career journey.
   - This feature should create interactive timelines of work history with company information, role descriptions, duration, and key accomplishments for each position.

4. **Interactive Code Demonstrations**: Showcase programming capabilities with runnable examples.
   - The most effective way to demonstrate coding ability is through actual code examples, so Hiroshi needs to include interactive code samples that potential employers can explore.
   - The system must embed runnable code snippets in various languages with syntax highlighting, execution capability, and results display without requiring server-side processing.

5. **Professional Endorsement Display**: Feature recommendations from colleagues and clients.
   - Social proof through endorsements from professional contacts strengthens Hiroshi's portfolio, providing third-party validation of his skills and work ethic.
   - This feature should present testimonials and endorsements with proper attribution, relationship context, and organization by skill or project area.

## Technical Requirements

### Testability Requirements
- GitHub integration must be testable with mock repository data
- Skills visualization must verify correct categorization and presentation
- Work history timeline must validate chronological accuracy and data relationships
- Code demonstration functionality must verify execution and output display
- Endorsement display must validate proper attribution and organization

### Performance Expectations
- Complete site generation should finish in under 10 seconds for a typical portfolio
- GitHub repository synchronization should process 50+ repositories in under 15 seconds
- Code example execution should return results in under 3 seconds
- Skills visualization should process 100+ individual skills in under 2 seconds
- Incremental builds should update changed content in under 3 seconds

### Integration Points
- GitHub API for repository data and statistics
- Code execution environments for different programming languages
- Timeline visualization libraries for work history
- Skill categorization systems and visualization tools
- Markdown and code parsing libraries

### Key Constraints
- Must operate without a database or server-side processing
- Must generate completely static output deployable to GitHub Pages or similar services
- Must respect GitHub API rate limits and implement proper caching
- Must support client-side only code execution for demonstrations
- Must optimize load time and performance for recruiter evaluation

## Core Functionality

The system should implement a comprehensive platform for developer portfolio websites:

1. **GitHub Integration Engine**
   - Fetch repository data from GitHub API
   - Process readme content and project descriptions
   - Extract language statistics and contribution metrics
   - Generate featured project showcases

2. **Skills Management System**
   - Process structured skill information with proficiency levels
   - Categorize skills by type (languages, frameworks, etc.)
   - Generate visual representations of skill distribution
   - Create relationship mapping between skills and projects

3. **Career Timeline Framework**
   - Process work history information chronologically
   - Generate interactive timeline visualization
   - Create detailed role and accomplishment descriptions
   - Link positions to relevant projects and skills

4. **Code Demonstration Platform**
   - Parse and process code snippets in various languages
   - Implement client-side execution environments
   - Provide syntax highlighting and formatting
   - Display execution results and output

5. **Endorsement Management**
   - Process recommendation and testimonial content
   - Validate attribution and relationship information
   - Organize endorsements by skill area or project
   - Generate presentation components for social proof

## Testing Requirements

### Key Functionalities to Verify
- GitHub repository data synchronization and presentation
- Skills categorization and visualization generation
- Work history timeline with chronological accuracy
- Code snippet execution in supported languages
- Endorsement display with proper attribution

### Critical User Scenarios
- Setting up a new developer portfolio with GitHub integration
- Showcasing a diverse set of technical skills with proficiency levels
- Presenting career progression through work history timeline
- Creating interactive code demonstrations in multiple languages
- Featuring professional endorsements from colleagues

### Performance Benchmarks
- Synchronize data from 50 GitHub repositories in under 15 seconds
- Generate skills visualization for 100+ individual skills in under 2 seconds
- Process 10+ work positions with details in under 3 seconds
- Execute code examples with results in under 3 seconds per example
- Complete full site generation for a typical portfolio in under 10 seconds

### Edge Cases and Error Conditions
- Handling GitHub API rate limiting and service disruptions
- Managing very large repositories or complex project structures
- Processing unusual career paths or concurrent positions
- Dealing with unsupported languages for code execution
- Handling missing or incomplete endorsement information

### Required Test Coverage Metrics
- Minimum 90% line coverage for core processing components
- 100% coverage for GitHub integration functionality
- Integration tests for all GitHub API interactions
- Validation tests for code execution and output
- Performance tests for repository synchronization

## Success Criteria

The implementation will be considered successful if it:

1. Automatically synchronizes and showcases GitHub repositories with comprehensive project information
2. Creates clear, visually appealing representations of technical skills with appropriate categorization
3. Generates an interactive timeline of work history showing career progression and accomplishments
4. Provides functioning code demonstrations in at least 5 common programming languages
5. Presents professional endorsements with proper attribution and context
6. Processes a typical developer portfolio (20 projects, 50+ skills, 5-10 work positions) in under 10 seconds
7. Achieves all required test coverage metrics with a clean test suite

## Getting Started

To set up the development environment:

1. Initialize the project using `uv init --lib` in your project directory
2. Install dependencies using `uv sync`
3. Run Python scripts with `uv run python your_script.py`
4. Run tests with `uv run pytest`

When implementing this library, focus on creating well-defined APIs that provide all the required functionality without any user interface components. All features should be implementable as pure Python modules and classes that can be thoroughly tested using pytest.