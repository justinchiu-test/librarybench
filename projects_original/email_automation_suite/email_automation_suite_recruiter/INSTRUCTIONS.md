# Recruiter Email Automation Suite

## Overview
TalentMail is a specialized email automation library designed for independent recruiters who manage communications between candidates and clients throughout the hiring process. It enables efficient tracking of candidate interactions, streamlined interview scheduling, organized communications by position, professional candidate presentations, and automated stage-based communications, allowing recruiters to manage multiple hiring pipelines simultaneously with precision and professionalism.

## Persona Description
Alex works as a recruitment consultant connecting candidates with companies and managing the entire hiring process via email. His primary goal is to track candidate and client communications throughout the hiring pipeline while sending timely updates to all parties.

## Key Requirements

1. **Candidate Tracking and Resume Management System**
   - Organize candidate communications with resume attachment management
   - Implement skill tagging and searchable candidate profiles
   - Track candidate status and interaction history
   - This feature is critical because it creates a searchable database of candidates with relevant skills and experience, allowing the recruiter to quickly identify suitable candidates for new positions while maintaining a complete history of all interactions

2. **Interview Scheduling Coordination Engine**
   - Manage interview scheduling between candidates and hiring companies
   - Generate automatic follow-up reminders for scheduled interviews
   - Track interview outcomes and feedback
   - This feature is essential because it streamlines the complex task of coordinating schedules between candidates and multiple stakeholders at client companies, ensuring all parties are properly prepared and reducing the risk of missed interviews

3. **Position-based Email Threading System**
   - Organize all communications related to specific job openings
   - Link candidates to their respective position applications
   - Maintain complete communication histories by position
   - This feature is vital because it allows the recruiter to maintain clear organization of all communications related to each open position, preventing confusion and ensuring that all candidate-position relationships are properly tracked

4. **Client Update and Candidate Presentation System**
   - Create professional candidate presentations for clients
   - Generate customizable candidate comparison reports
   - Provide structured updates on hiring pipeline status
   - This feature is important because it enables the recruiter to consistently present candidates to clients in a professional, branded format that highlights relevant qualifications, streamlining the client's review process and strengthening the recruiter's value proposition

5. **Hiring Stage Automation with Communication Sequences**
   - Define multi-stage hiring pipelines with appropriate messaging for each stage
   - Automatically trigger communications based on candidate stage transitions
   - Track candidates through the complete hiring lifecycle
   - This feature ensures candidates and clients receive appropriate, timely communications as candidates progress through different stages of the hiring process, maintaining engagement while reducing the manual effort of sending stage-appropriate updates

## Technical Requirements

### Testability Requirements
- All email generation and categorization functions must be testable with mock data
- Resume parsing and skill tagging must be verifiable with sample resumes
- Interview scheduling logic must be testable with simulated calendar scenarios
- Position linking and organization must be testable with multiple candidate-position relationships
- Stage-based communication triggering must be verifiable with test pipeline progressions

### Performance Expectations
- Candidate tracking should efficiently handle databases of at least 1000 candidates
- Interview scheduling should process at least 50 interview requests per day
- Position-based organization should support at least 100 active positions simultaneously
- Candidate presentation generation should complete in under 500ms per candidate
- The system should handle at least 30 active hiring pipelines without performance degradation

### Integration Points
- IMAP and SMTP libraries for email retrieval and sending
- Template engine for dynamic content generation
- SQLite or similar database for candidate and position information
- Calendar system for interview scheduling
- Basic text processing for resume parsing and skill extraction

### Key Constraints
- All candidate data must be handled in compliance with privacy regulations
- Client communications must maintain consistent professional branding
- The system must be resilient to scheduling conflicts and changes
- Resume and attachment handling must be secure and efficient
- The implementation must respect email rate limits and anti-spam requirements

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core of the Recruiter Email Automation Suite should provide:

1. **Candidate Management Engine**
   - Processing and organizing candidate information and resumes
   - Extracting and tagging skills and qualifications
   - Tracking candidate status and interactions
   - Supporting search and filtering of the candidate database

2. **Position Management System**
   - Maintaining position requirements and status
   - Linking candidates to appropriate positions
   - Tracking position-specific communication histories
   - Supporting position pipeline analytics

3. **Interview Coordination Module**
   - Managing interview scheduling between candidates and clients
   - Generating interview confirmation and preparation materials
   - Sending automated reminders to all parties
   - Tracking interview results and feedback

4. **Client Communication Engine**
   - Creating professional candidate presentations
   - Generating position status updates
   - Managing client-specific communication preferences
   - Tracking client engagement and feedback

5. **Hiring Pipeline Workflow**
   - Defining and managing multi-stage hiring processes
   - Transitioning candidates between pipeline stages
   - Triggering stage-appropriate communications
   - Analyzing pipeline efficiency and conversion metrics

## Testing Requirements

### Key Functionalities to Verify
- Candidate information extraction and organization from emails
- Interview scheduling coordination between multiple parties
- Position-based email organization and threading
- Candidate presentation generation for clients
- Stage-based communication triggering in hiring pipelines

### Critical User Scenarios
- Processing a new candidate application with resume attachment
- Coordinating and confirming an interview between a candidate and client
- Organizing multiple candidate communications for a specific position
- Generating professional candidate presentations for client review
- Managing a candidate's progression through a multi-stage hiring pipeline

### Performance Benchmarks
- Resume processing should complete in under 1 second per resume
- Interview scheduling should handle coordination between 5+ parties efficiently
- Position organization should support at least.100 active positions
- Candidate presentation generation should complete in under 500ms
- The system should handle at least 30 concurrent hiring pipelines without degradation

### Edge Cases and Error Conditions
- Handling candidates applying for multiple positions
- Managing interview rescheduling and cancellations
- Processing position requirement changes mid-pipeline
- Dealing with incomplete candidate information
- Handling client feedback that affects multiple candidates

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of resume processing and skill extraction
- 100% coverage of interview scheduling coordination
- 100% coverage of candidate presentation generation
- Minimum 95% coverage of pipeline stage transition logic

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

- Candidate tracking accurately processes and organizes test candidate data
- Interview scheduling correctly coordinates test interview scenarios
- Position-based threading properly organizes communications by open role
- Candidate presentations are professionally generated with appropriate information
- Hiring stage automation correctly triggers communications based on pipeline progress
- All performance benchmarks are met under load testing
- The system correctly handles all specified edge cases and error conditions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Getting Started
To set up the development environment:
1. Create a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: When testing your implementation, you MUST run tests with pytest-json-report and provide the pytest_results.json file:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

Providing the pytest_results.json file is MANDATORY for demonstrating that your implementation meets the requirements.