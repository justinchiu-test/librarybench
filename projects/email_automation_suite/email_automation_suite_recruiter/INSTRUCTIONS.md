# RecruitMailFlow - Recruitment Email Management System

## Overview
RecruitMailFlow is a specialized email automation system designed for independent recruiters who need to efficiently manage candidate communications, job openings, interview scheduling, client updates, and placement tracking. The system streamlines the entire recruitment process through intelligent email categorization, applicant tracking, interview coordination, and client reporting to maximize placement success while minimizing administrative overhead.

## Persona Description
Alex works as a recruitment consultant connecting candidates with companies and managing the entire hiring process via email. His primary goal is to track candidate and client communications throughout the hiring pipeline while sending timely updates to all parties.

## Key Requirements

1. **Candidate Tracking with Resume Management**
   - Implement intelligent resume extraction and parsing from email attachments
   - Create candidate profiles with skill tagging based on resume content
   - Organize communications by candidate and maintain conversation history
   - Enable advanced candidate search by skills, experience, and requirements
   - This feature is critical because it transforms unstructured resume data into searchable candidate profiles, enabling quick matching to opportunities while maintaining complete communication history for relationship management.

2. **Interview Scheduling and Confirmation System**
   - Create automated interview coordination emails with availability options
   - Send confirmation and reminder sequences to candidates and hiring managers
   - Track interview status and follow-up requirements
   - Handle rescheduling requests and conflicts efficiently
   - This feature is essential because interview coordination typically consumes 30-40% of a recruiter's time, with complex scheduling across multiple parties that can be largely automated to focus attention on high-value activities.

3. **Position-Based Email Threading and Organization**
   - Organize all communications related to specific job openings
   - Link candidates to appropriate openings with status tracking
   - Maintain position requirement details and hiring progress
   - Enable cross-referencing between positions with similar requirements
   - This feature is vital because keeping communications organized by position prevents confusion, ensures all candidates are properly tracked, and provides clear visibility into the status of each opening.

4. **Client Update and Candidate Presentation System**
   - Generate professional candidate presentation templates
   - Create customizable client update reports on hiring progress
   - Schedule regular client communication based on hiring urgency
   - Track client feedback and hiring manager preferences
   - This feature is crucial because presenting candidates professionally and keeping clients informed about hiring progress in a consistent, timely manner dramatically improves client satisfaction and increases placement rates.

5. **Hiring Stage Automation and Milestone Tracking**
   - Define customizable hiring pipeline stages for different clients and positions
   - Trigger stage-appropriate communications automatically
   - Track milestone completion and time-in-stage metrics
   - Generate alerts for stalled processes or required interventions
   - This feature is invaluable because it ensures no candidate falls through the cracks, maintains momentum in the hiring process, and provides valuable analytics on pipeline efficiency and bottlenecks.

## Technical Requirements

### Testability Requirements
- All email classification and routing must be testable with mock recruitment messages
- Resume parsing accuracy must be measurable with test resumes
- Template variable substitution must be verifiable with different candidate and position data
- Pipeline stage progression must be testable with simulated hiring scenarios
- All scheduling operations must be verifiable with test calendar data

### Performance Expectations
- Email processing and classification must complete in under 400ms per message
- Resume parsing and skill extraction must complete in under 3 seconds per resume
- The system must handle at least 100 active candidates across 20 open positions
- Search operations must return results in under 1 second across 5,000+ candidate profiles
- Report generation must complete in under 10 seconds for client updates

### Integration Points
- IMAP/SMTP support for connecting to standard email providers
- Calendar integration for interview scheduling
- ATS/CRM integration options for extended recruitment management
- Document parsing capabilities for resume and job description analysis
- Optional job board integration for posting and application collection

### Key Constraints
- All candidate personal information must be securely stored and handled
- Client confidentiality must be maintained when dealing with sensitive positions
- The system must function without reliance on expensive third-party services
- Email operations must be fault-tolerant to prevent missed communications
- The system must be operable by users with limited technical expertise

## Core Functionality

RecruitMailFlow must provide a comprehensive API for email management focused on recruitment operations:

1. **Email Processing Engine**
   - Connect to email accounts via IMAP/SMTP
   - Apply classification rules to incoming messages
   - Categorize communications by candidate, client, and position
   - Extract and process resume attachments automatically

2. **Candidate Management System**
   - Parse and analyze resume content for skills and experience
   - Maintain candidate profiles with status and history
   - Track candidate progression through hiring pipelines
   - Manage communication history and engagement metrics

3. **Position and Client Database**
   - Store position requirements and status information
   - Track client preferences and hiring patterns
   - Maintain hiring manager contacts and communication preferences
   - Monitor position filling progress and milestone achievement

4. **Interview Coordination System**
   - Manage scheduling and calendar availability
   - Generate appropriate interview communications
   - Send reminders and confirmations to all parties
   - Track interview outcomes and feedback

5. **Reporting and Analytics Engine**
   - Generate client-ready candidate presentations
   - Create hiring progress reports with key metrics
   - Track pipeline efficiency and conversion rates
   - Provide insights for recruitment process improvement

## Testing Requirements

### Key Functionalities to Verify
- Email classification accuracy must be >90% for typical recruitment communications
- Resume parsing must correctly extract key skills and experience with >85% accuracy
- Template variable substitution must work correctly across all recruitment templates
- Pipeline stage tracking must accurately reflect candidate progression
- Interview scheduling must correctly handle availability conflicts and rescheduling

### Critical User Scenarios
- A new job opening is received from a client and set up in the system
- A candidate submits a resume that is automatically parsed and profiled
- An interview is coordinated between a candidate and hiring manager
- A client receives a professional presentation of qualified candidates
- A candidate progresses through the entire recruitment pipeline to placement

### Performance Benchmarks
- System must handle at least 200 incoming candidate emails per day
- Resume parsing must process at least 50 resumes per hour
- Search operations must maintain sub-second response with 10,000+ stored profiles
- Interview scheduling must support at least 30 interview arrangements per day
- Report generation must support at least 20 client updates per day

### Edge Cases and Error Conditions
- System must handle unusual resume formats and attachments
- Interview scheduling must gracefully handle timezone differences and conflicts
- Candidate withdrawal mid-process must be properly reflected in all reports
- The system must gracefully handle email server connection failures
- Position requirement changes must be appropriately propagated to candidate matching

### Required Test Coverage Metrics
- Unit test coverage must exceed 90% for all core modules
- Integration tests must verify all system components working together
- Performance tests must validate system under high-volume recruitment scenarios
- Security tests must verify proper handling of candidate personal information
- Regression tests must ensure functionality is preserved across updates

## Success Criteria

A successful implementation of RecruitMailFlow will meet the following criteria:

1. **Efficiency Improvements**
   - Reduce time spent on email management by at least 70%
   - Decrease time-to-fill positions by at least 30%
   - Automate at least 80% of routine recruitment communications

2. **Business Impact**
   - Increase candidate placement rate by at least 25%
   - Improve client satisfaction scores by at least 40%
   - Enable management of 50% more open positions simultaneously
   - Reduce interview no-show rate by at least 80%

3. **Technical Quality**
   - Pass all specified test requirements with >90% coverage
   - Meet or exceed all performance expectations
   - Provide a clean, well-documented API that could be extended
   - Operate reliably without unexpected crashes or data loss
   - Maintain security and confidentiality of candidate and client information

4. **User Experience**
   - Enable processing of new job openings in under 5 minutes
   - Allow candidate profile creation from resume in under 2 minutes
   - Provide clear visibility into recruitment pipeline status
   - Generate professional client-ready reports automatically

To set up your development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.