# JournalistBrain: Knowledge Management System for Investigative Journalists

## Overview
JournalistBrain is a specialized personal knowledge management system designed for investigative journalists who need to track complex stories, manage sensitive sources, organize evidence, and develop multiple narrative angles while maintaining the highest standards of journalistic integrity and source protection.

## Persona Description
Chen investigates complex stories involving government policy, corporate behavior, and public impact. He needs to connect sources, documents, and interviews while tracking the evolution of developing narratives.

## Key Requirements
1. **Source relationship mapping**: Create and visualize networks of information sources, tracking reliability, connections, and potential conflicts of interest. This feature is critical for establishing the credibility of gathered information, identifying patterns of corroboration or contradiction between sources, and maintaining clear attribution chains throughout the investigative process.

2. **Evidence strength assessment**: Evaluate and track the supporting documentation for each claim or allegation, creating a hierarchy of evidence quality. This capability helps Chen distinguish between verified facts, credible allegations, and unsubstantiated claims, ensuring reporting meets high journalistic standards and can withstand legal scrutiny or challenges to accuracy.

3. **Chronological investigation tracking**: Map how information emerges over time, highlighting evolving understanding and new revelations during ongoing investigations. This timeline-based approach helps identify information gaps, track the changing narrative as new evidence emerges, and maintain a clear picture of what was known when during long-running investigations.

4. **Narrative development workspaces**: Organize material for different potential story angles, testing multiple interpretations of the same underlying evidence. This feature enables exploration of different narrative approaches to complex stories, helps identify the most compelling and well-supported angles, and facilitates collaboration with editors on story structure.

5. **Secure source protection**: Implement compartmentalized storage of sensitive information with special protections for confidential sources and whistleblowers. This capability is essential for fulfilling the ethical obligation to protect vulnerable sources, meeting legal requirements for source confidentiality, and maintaining source trust in highly sensitive investigations.

## Technical Requirements
- **Testability requirements**:
  - All relationship mapping functions must be independently testable
  - Evidence assessment algorithms must be verifiable against journalistic standards
  - Chronological tracking must be validated for accuracy and completeness
  - Narrative organizing tools must be tested for different story structures
  - Source protection measures must be verifiable for security and reliability

- **Performance expectations**:
  - System must efficiently handle data for investigations with 100+ sources and 1000+ documents
  - Relationship visualization should render in under 3 seconds
  - Evidence assessment should process 50+ documents per minute
  - Full-text search across all investigation materials should return results in under 2 seconds
  - Secure compartments must verify access authorization in under 500ms

- **Integration points**:
  - Plain text and Markdown file support
  - Document analysis and annotation systems
  - Secure storage for sensitive materials
  - Timeline visualization generation
  - Export capabilities for story drafting

- **Key constraints**:
  - All data must be stored locally in accessible, plain-text formats
  - No dependency on external web services for core functionality
  - Must support secure offline operation
  - Must maintain absolute integrity of source protection mechanisms
  - Must support evidence chains that would stand up to editorial and legal review

## Core Functionality
The system must implement a comprehensive knowledge management foundation with specialized features for investigative journalism:

1. **Source Management System**:
   - Create detailed source profiles with reliability assessment
   - Track relationships between sources and potential conflicts of interest
   - Manage contact information with appropriate security measures
   - Document source attribution for each piece of information

2. **Evidence Organization Framework**:
   - Catalog and categorize documents, interviews, and other evidence
   - Assess evidence quality and corroboration status
   - Link evidence to specific claims and narrative elements
   - Track verification status and required follow-up

3. **Investigation Timeline Management**:
   - Create chronologies of both events being investigated and the investigation itself
   - Track when information became known to the investigation team
   - Identify gaps and inconsistencies in chronological understanding
   - Map evolution of key narrative elements over time

4. **Narrative Development System**:
   - Create workspaces for exploring different story angles
   - Organize evidence and sources according to narrative relevance
   - Identify strongest supported elements across potential narratives
   - Track editorial decisions and story evolution

5. **Security and Source Protection**:
   - Implement compartmentalized storage for sensitive information
   - Create security levels with appropriate access controls
   - Generate source-protected exports for editorial review
   - Maintain secure backup and recovery mechanisms

## Testing Requirements
The implementation must be thoroughly testable with comprehensive pytest coverage:

- **Key functionalities that must be verified**:
  - Source relationship mapping correctly identifies connections and potential conflicts
  - Evidence assessment accurately classifies documentation strength and verification status
  - Chronological tracking properly orders information discovery and event timelines
  - Narrative workspaces effectively organize material for different story approaches
  - Source protection measures completely secure sensitive information

- **Critical user scenarios that should be tested**:
  - Building a complex source network with reliability assessment
  - Evaluating evidence strength for controversial claims
  - Tracking information discovery during a long-running investigation
  - Developing multiple narrative angles from the same evidence base
  - Protecting confidential source information while maintaining usability

- **Performance benchmarks that must be met**:
  - Sub-second response time for most knowledge retrieval operations
  - Efficient handling of investigations with hundreds of sources and thousands of documents
  - Responsive visualization of complex source and evidence networks
  - Memory-efficient operation suitable for standard laptop environments

- **Edge cases and error conditions that must be handled properly**:
  - Contradictory information from similarly credible sources
  - Evidence of varying quality and reliability
  - Incomplete chronologies with timing uncertainties
  - Complex narrative structures with multiple interrelated threads
  - High-risk source situations requiring maximum security

- **Required test coverage metrics**:
  - Minimum 90% code coverage across all core modules
  - 100% coverage of source protection functionality
  - All public APIs must have comprehensive integration tests
  - All error handling paths must be explicitly tested

## Success Criteria
The implementation will be considered successful when it demonstrably:

1. Creates clear visualizations of source networks with reliability indicators and relationship mapping
2. Provides robust assessment of evidence quality with appropriate verification tracking
3. Accurately tracks both event chronologies and the evolution of the investigation itself
4. Enables effective organization of material for different narrative approaches and story angles
5. Implements impenetrable protection for confidential sources and sensitive information
6. Performs efficiently with large investigations containing numerous sources and documents
7. Preserves all data in accessible formats that ensure long-term availability and integrity
8. Passes all specified tests with the required code coverage metrics

To set up the development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install required dependencies
uv sync
```