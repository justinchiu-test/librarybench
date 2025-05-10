# TalentFlow - Recruitment Pipeline Email Management System

## Overview
A specialized email automation system designed for independent recruiters that streamlines candidate tracking, interview scheduling, and client updates throughout the hiring process, focusing on organizing communications by job opening and maintaining a structured recruitment pipeline.

## Persona Description
Alex works as a recruitment consultant connecting candidates with companies and managing the entire hiring process via email. His primary goal is to track candidate and client communications throughout the hiring pipeline while sending timely updates to all parties.

## Key Requirements

1. **Candidate Tracking with Resume Management**
   - Automatic extraction and organization of resume attachments
   - Skill and experience tagging system based on resume content analysis
   - Searchable candidate database integrated with email history
   - This feature is essential for Alex to quickly access candidate information when communicating with clients, eliminating the need to manually search through emails for resumes and enabling skill-based matching to new positions.

2. **Interview Scheduling Coordination**
   - Automated scheduling follow-up sequences
   - Confirmation tracking for interview times
   - Reminder generation for all parties before interviews
   - This feature allows Alex to efficiently coordinate interviews between candidates and clients without manually tracking multiple calendar availabilities, reducing scheduling conflicts and ensuring all parties receive appropriate reminders.

3. **Position-Based Email Threading**
   - Automatic organization of emails by job opening
   - Linking of candidate communications to specific positions
   - Status tracking for each position (open, interviewing, filled)
   - This feature enables Alex to maintain a clear overview of all communications related to each job opening, making it easy to track progress and quickly access relevant conversations when clients request updates.

4. **Client Update Templates**
   - Customizable candidate presentation formats
   - Batch update capabilities for sending multiple candidate profiles
   - Template performance tracking to optimize response rates
   - This feature allows Alex to consistently present candidates in a professional, branded format tailored to each client's preferences, saving time on formatting and improving the impact of candidate presentations.

5. **Hiring Stage Automation**
   - Stage-based communication workflows (initial contact, screening, interview, offer, onboarding)
   - Milestone-triggered email sequences
   - Status dashboard showing candidates at each pipeline stage
   - This feature ensures consistent communication throughout the hiring process with appropriate message content for each stage, eliminating manual tracking of where each candidate stands in the recruitment pipeline.

## Technical Requirements

### Testability Requirements
- All components must be testable without requiring actual email server connections
- Mock objects must be available for IMAP/SMTP services
- Resume parsing functionality must be testable with sample documents
- Scheduling logic must be verifiable with time manipulation
- Pipeline stage transitions must be testable with event triggers

### Performance Expectations
- Resume parsing and tagging should complete within 10 seconds per document
- Email classification and filing should occur within 3 seconds
- Search across candidate database should return results within 2 seconds
- The system should handle up to 200 active positions and 1000 candidates
- Daily email volume of up to 300 incoming and 200 outgoing messages

### Integration Points
- IMAP and SMTP protocols for email server communication
- Local database for storing templates, position details, and candidate information
- File system for managing resume attachments and other documents
- Text extraction system for parsing resume content
- Export/import functionality for backup and data migration

### Key Constraints
- Must work with standard email protocols (IMAP/SMTP)
- Must handle various document formats for resumes (PDF, DOCX, RTF, TXT)
- Must maintain candidate privacy and comply with data protection regulations
- Must operate efficiently on standard hardware without requiring cloud resources
- All data must be stored locally with proper backup procedures

## Core Functionality

The system must provide:

1. **Email Processing Engine**
   - Connect to email accounts via IMAP
   - Process incoming messages with rule-based classification
   - Identify job positions and candidates from email content
   - Organize conversations by position and candidate

2. **Resume Management System**
   - Extract content from various document formats
   - Parse skills, experience, and education information
   - Generate candidate profiles with extracted data
   - Enable searching across candidate qualifications

3. **Recruitment Pipeline Tracking**
   - Define customizable pipeline stages for hiring process
   - Track candidate progression through stages
   - Trigger appropriate communications at each stage
   - Generate pipeline status reports for clients

4. **Interview Coordination System**
   - Parse availability information from emails
   - Generate scheduling proposals based on constraints
   - Send confirmation and reminder messages
   - Track interview status and outcomes

5. **Client Relationship Management**
   - Store client company information and preferences
   - Track communication history by client
   - Manage position requirements and status
   - Generate client-ready candidate presentations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of resume parsing and skill extraction
- Email classification for different hiring stages
- Template rendering with various candidate profiles
- Pipeline stage tracking and transitions
- Attachment handling for different document types

### Critical Scenarios to Test
- Processing a new job opening from a client
- Handling a new candidate application
- Coordinating interview scheduling between parties
- Presenting multiple candidates for a position
- Managing a candidate through the entire pipeline

### Performance Benchmarks
- Resume parsing accuracy of at least 90% for key fields
- Email classification accuracy of at least 95%
- Search response time under 1 second for candidate qualification queries
- System memory usage under 500MB with 500 active candidates
- Database query performance with large datasets (5,000+ emails)

### Edge Cases and Error Conditions
- Handling malformed or non-standard resume formats
- Processing emails with ambiguous position or candidate references
- Managing conflicting interview scheduling requests
- Dealing with candidates applying for multiple positions
- Handling position requirement changes mid-process
- Recovering from interrupted pipeline sequences

### Required Test Coverage
- Minimum 90% code coverage for core functionality
- 100% coverage of resume parsing logic
- 100% coverage of pipeline stage transition logic
- 100% coverage of template rendering engine
- Comprehensive integration tests for full recruitment workflows

## Success Criteria

The implementation will be considered successful if it:

1. Reduces candidate processing time by at least 60%
2. Ensures consistent communication at each stage of the hiring process
3. Creates a searchable candidate database that accurately reflects skills and experience
4. Reduces interview scheduling time by at least 75%
5. Enables tracking of at least 50 active positions simultaneously
6. Provides clear visibility into candidate pipeline stages
7. Successfully classifies at least 90% of incoming emails automatically
8. Reduces email management time by at least 20 hours per week

## Development Setup

To set up the development environment:

1. Initialize a new project with UV:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run the code:
   ```
   uv run python your_script.py
   ```

4. Run tests:
   ```
   uv run pytest
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