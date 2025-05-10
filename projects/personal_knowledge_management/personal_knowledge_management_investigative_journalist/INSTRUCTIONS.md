# InvestigatePro - Journalistic Investigation Management System

A specialized personal knowledge management system for investigative journalists to track sources, evidence, and developing narratives while ensuring source protection.

## Overview

InvestigatePro is a comprehensive knowledge management system designed specifically for investigative journalists who need to organize complex stories involving government policy, corporate behavior, and public impact. The system excels at managing sources, documents, interviews, and fact patterns while maintaining strict information security for sensitive sources. It emphasizes evidence verification, chronological tracking, narrative development, and the creation of multiple story angles while ensuring journalistic integrity and source protection throughout the investigation process.

## Persona Description

Chen investigates complex stories involving government policy, corporate behavior, and public impact. He needs to connect sources, documents, and interviews while tracking the evolution of developing narratives.

## Key Requirements

1. **Source relationship mapping**: Build structured networks tracking information provenance and credibility assessment.
   - Critical for Chen to maintain clear understanding of where information originated
   - Enables evaluation of source reliability and potential biases
   - Helps identify information corroborated by multiple independent sources
   - Facilitates protection of sensitive sources through relationship obfuscation
   - Supports journalistic integrity by maintaining clear information provenance

2. **Evidence strength assessment**: Create systematic linking between claims and supporting documentation.
   - Essential for evaluating the factual basis of investigative conclusions
   - Enables prioritization of claims based on substantiation level
   - Helps identify gaps requiring additional reporting or documentation
   - Facilitates legal review and pre-publication fact-checking
   - Supports defensible reporting with clear evidentiary foundations

3. **Chronological investigation tracking**: Document how information emerged over time and evolving understanding.
   - Vital for reconstructing complex event sequences accurately
   - Enables identification of causal relationships between events
   - Helps reveal patterns and timelines that might otherwise remain hidden
   - Facilitates understanding of how the investigation itself evolved
   - Supports narrative development with clear temporal frameworks

4. **Narrative development workspaces**: Organize information for different potential story angles and approaches.
   - Crucial for exploring multiple interpretations of complex factual patterns
   - Enables efficient reorganization of information for different publishing formats
   - Helps identify the most compelling and well-supported narrative approaches
   - Facilitates collaboration with editors on story development
   - Supports comprehensive reporting that considers multiple perspectives

5. **Secure source protection**: Implement compartmentalized storage for sensitive source information and communications.
   - Essential for protecting vulnerable sources from identification
   - Enables appropriate handling of information based on sensitivity
   - Helps maintain source confidentiality throughout the investigation
   - Facilitates secure communication with confidential sources
   - Supports ethical journalistic practices and source trust maintenance

## Technical Requirements

### Testability Requirements
- All functionality must be implemented as testable Python modules without UI dependencies
- Test data generators should create realistic journalistic scenarios, source networks, and evidence collections
- Mock source databases should demonstrate perfect separation of identifying information
- Evidence assessment algorithms must produce consistent, verifiable strength ratings
- Security mechanisms must be verifiable through penetration testing approaches

### Performance Expectations
- Source relationship visualization should handle networks with 100+ sources
- Evidence assessment should process 500+ documents in under 5 seconds
- Timeline reconstruction should manage 1000+ dated events in under 2 seconds
- Narrative workspace switching should reorganize information in under 1 second
- Security mechanisms should enforce perfect compartmentalization with no information leakage

### Integration Points
- Plain text and Markdown file system storage with strong encryption
- Secure document storage with access control
- Structured data export for editorial review (with appropriate redactions)
- Timeline visualization capabilities
- Optional integration with secure communication channels

### Key Constraints
- All sensitive data must be stored with strong encryption and compartmentalization
- No external API dependencies for core functionality that might compromise security
- System must be usable offline for source meetings and field reporting
- Data structures must implement perfect confidentiality for source protection
- Must support rapid knowledge retrieval during interviews and on deadline

## Core Functionality

The InvestigatePro system should implement the following core functionality:

1. **Source Management System**
   - Create and track sources with reliability assessment
   - Map relationships between sources and their information
   - Implement multi-level source protection protocols
   - Document source motivation and potential biases
   - Track source contact history and communications

2. **Evidence Repository**
   - Catalog and organize documents, recordings, and data
   - Link evidence to specific claims and allegations
   - Assess evidence strength and corroboration level
   - Track chain of custody for sensitive materials
   - Implement secure storage with appropriate access controls

3. **Investigation Timeline Framework**
   - Create chronological event sequences with source attribution
   - Document when information became known to the investigation
   - Track evolving understanding of key events over time
   - Identify critical timeline gaps requiring additional reporting
   - Visualize complex temporal relationships

4. **Narrative Development System**
   - Create multiple story frameworks for different angles
   - Organize evidence and sources by narrative relevance
   - Track supporting evidence strength for each narrative element
   - Identify compelling narrative structures from factual patterns
   - Support various output formats (longform, series, multimedia)

5. **Security and Source Protection**
   - Implement encrypted storage for sensitive information
   - Create information compartments with strict access controls
   - Develop protocols for source anonymization in notes
   - Establish secure communication channels for vulnerable sources
   - Provide security breach detection and response mechanisms

6. **Fact-Checking Framework**
   - Systematically verify claims against supporting evidence
   - Implement multi-level verification protocols
   - Track verification status for all significant assertions
   - Document verification methodology and limitations
   - Support pre-publication legal review with evidence mapping

7. **Knowledge Discovery**
   - Implement full-text search with security-aware permissions
   - Find connections between seemingly unrelated facts
   - Identify patterns across different information sources
   - Generate investigation status reports for editorial review
   - Support complex queries while maintaining security boundaries

## Testing Requirements

### Key Functionalities to Verify
- Source relationship mapping accuracy and security
- Evidence strength assessment consistency and reliability
- Chronological reconstruction fidelity and completeness
- Narrative workspace organization and information accessibility
- Source protection mechanism effectiveness
- Cross-investigation search functionality with security constraints
- Information relationship integrity and accuracy

### Critical User Scenarios
- Investigating a complex corporate malfeasance case with whistleblowers
- Tracking a government policy change through multiple administrations
- Managing confidential sources in a sensitive political investigation
- Organizing evidence for a multi-part investigative series
- Preparing for an interview with a key source or subject
- Responding to pre-publication legal challenges
- Collaborating with editors while protecting source identities

### Performance Benchmarks
- Source network visualization with 150+ entities in under 2 seconds
- Evidence assessment for 1000+ documents in under 10 seconds
- Timeline reconstruction with 2000+ events in under 3 seconds
- Narrative workspace reorganization in under 1 second
- Full-text search with security filtering in under 2 seconds

### Edge Cases and Error Conditions
- Handling anonymous or pseudonymous sources
- Managing conflicting accounts from different sources
- Resolving timeline inconsistencies and contradictions
- Recovering from security compartment failures
- Handling extremely sensitive whistleblower information
- Managing retractions or corrections to previously collected information
- Processing extremely large document collections (10,000+ files)

### Test Coverage Requirements
- Minimum 95% code coverage for core functionality
- 100% coverage of security and source protection mechanisms
- 100% coverage of evidence assessment algorithms
- 100% coverage of timeline reconstruction functions
- Integration tests for end-to-end investigative workflow scenarios

## Success Criteria

The implementation will be considered successful when it:

1. Enables the journalist to create comprehensive source networks with clear reliability assessment while maintaining strict source protection.

2. Provides robust evidence strength evaluation that connects claims to supporting documentation with clear assessment of corroboration level.

3. Facilitates detailed chronological tracking that accurately represents how events unfolded and when information became known.

4. Supports flexible narrative development with the ability to organize information for different story angles and publishing formats.

5. Implements unbreakable source protection with perfect compartmentalization of sensitive source information.

6. Achieves all performance benchmarks with large investigative databases containing thousands of documents and hundreds of sources.

7. Maintains perfect security with robust protection mechanisms for sensitive information.

8. Enables the discovery of non-obvious connections and patterns within complex factual scenarios.

9. Passes all specified test requirements with the required coverage metrics.

10. Operates completely offline with all data stored securely for both source protection and accessibility during field reporting.