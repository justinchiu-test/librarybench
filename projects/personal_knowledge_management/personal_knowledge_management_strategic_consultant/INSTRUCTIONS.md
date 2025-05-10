# ConsultantBrain: Knowledge Management System for Strategic Consultants

## Overview
ConsultantBrain is a specialized personal knowledge management system designed for strategic consultants who need to manage insights across diverse industries and clients, leverage past experiences for new engagements, and maintain strict confidentiality while still recognizing valuable patterns across client work.

## Persona Description
Elena advises businesses across different industries, drawing connections between previous client experiences, market research, and emerging trends. She needs to leverage past insights for new client situations while maintaining strict confidentiality between engagements.

## Key Requirements
1. **Client information firewall**: Establish strict separation between client data while enabling pattern recognition and insight transfer without compromising confidentiality. This capability is essential for consultants who must adhere to strict confidentiality agreements while still benefiting from cross-client learning, ensuring that sensitive information remains properly compartmentalized.

2. **Industry framework application**: Track which strategic frameworks, analytical models, and business approaches are most effective in different industries and scenarios. This feature enables Elena to quickly identify relevant analytical approaches based on past successes, adapt proven methodologies to new contexts, and build a structured repository of consulting frameworks with their contextual applications.

3. **Engagement retrospective**: Capture structured lessons learned from completed consulting projects, including approach effectiveness, client challenges, and outcome assessment. This systematic knowledge capture helps avoid repeating past mistakes, builds a growing body of consulting wisdom, and enables continuous improvement in consulting methods and deliverables.

4. **Pattern recognition**: Identify relevant insights from past engagements that might apply to new client situations, suggesting connections that respect confidentiality boundaries. This capability helps Elena avoid "reinventing the wheel" for each new client, recognize non-obvious parallels between different industries, and leverage the firm's collective experience in a responsible manner.

5. **Anonymized case study generation**: Create shareable knowledge assets by automatically transforming client-specific insights into anonymized case studies that protect sensitive information. This feature helps Elena share valuable learnings with colleagues or clients without breaching confidentiality, demonstrate expertise without revealing sources, and build a library of teaching examples for internal training.

## Technical Requirements
- **Testability requirements**:
  - Information firewall integrity must be independently verifiable
  - Framework application recommendations must be testable against historical outcomes
  - Retrospective capture must maintain consistent structure and searchability
  - Pattern recognition algorithms must be validated for relevance and confidentiality
  - Anonymization processes must be verified for completeness and security

- **Performance expectations**:
  - System must efficiently handle data from 100+ client engagements
  - Pattern recognition should process engagement history in under 10 seconds
  - Framework recommendation should generate in under 3 seconds
  - Full-text search across all non-confidential knowledge should return results in under 2 seconds
  - Information firewall checks should verify access appropriateness in under 500ms

- **Integration points**:
  - Plain text and Markdown file support
  - Structured data import/export with confidentiality filtering
  - Version control for evolving knowledge assets
  - Access control and information classification system
  - Template system for structured knowledge capture

- **Key constraints**:
  - All data must be stored locally in accessible, plain-text formats
  - No dependency on external web services for core functionality
  - Must support offline operation
  - Must maintain absolute integrity of client confidentiality boundaries
  - Must prevent unintentional leakage of confidential information

## Core Functionality
The system must implement a comprehensive knowledge management foundation with specialized features for strategic consulting:

1. **Client Engagement Management**:
   - Create secure client workspaces with strict information boundaries
   - Classify information by confidentiality level and sharing permissions
   - Track client-specific context and requirements
   - Maintain engagement timelines and deliverable history

2. **Consulting Framework Organization**:
   - Catalog strategic frameworks, analytical models, and methodologies
   - Track framework effectiveness across different industries and scenarios
   - Document framework adaptations for specific client contexts
   - Provide guidance on framework selection based on engagement parameters

3. **Learning and Improvement System**:
   - Capture structured retrospectives from completed engagements
   - Identify success factors and improvement opportunities
   - Track evolving consulting approaches over time
   - Aggregate lessons learned into evolving best practices

4. **Cross-Engagement Intelligence**:
   - Identify patterns and insights across multiple engagements
   - Suggest relevant past experiences for new client situations
   - Analyze trends and evolving practices within industries
   - Generate confidentiality-safe insights from aggregate experience

5. **Knowledge Asset Development**:
   - Transform client-specific insights into anonymized reference materials
   - Create teaching cases from engagement experiences
   - Develop reusable content templates and frameworks
   - Build a library of confidentiality-safe consulting resources

## Testing Requirements
The implementation must be thoroughly testable with comprehensive pytest coverage:

- **Key functionalities that must be verified**:
  - Client information firewall prevents unauthorized cross-client data access
  - Industry framework application correctly matches approaches to contexts
  - Engagement retrospective captures comprehensive project learning
  - Pattern recognition identifies relevant connections while respecting confidentiality
  - Anonymization process completely removes identifying client information

- **Critical user scenarios that should be tested**:
  - Managing multiple concurrent client engagements with strict information separation
  - Selecting appropriate frameworks based on industry and engagement context
  - Capturing comprehensive retrospectives from completed projects
  - Receiving relevant insights from past work when starting a new engagement
  - Creating anonymized case studies suitable for sharing with colleagues

- **Performance benchmarks that must be met**:
  - Sub-second response time for most knowledge retrieval operations
  - Efficient handling of data from 100+ client engagements
  - Responsive pattern recognition across the entire engagement history
  - Memory-efficient operation suitable for standard laptop environments

- **Edge cases and error conditions that must be handled properly**:
  - Highly similar clients in the same industry requiring extra confidentiality measures
  - Conflicting lessons learned from different engagement experiences
  - Incomplete information from partial or abandoned projects
  - Complex confidentiality requirements with multiple stakeholders
  - Identifying information embedded in seemingly generic insights

- **Required test coverage metrics**:
  - Minimum 90% code coverage across all core modules
  - 100% coverage of confidentiality management functionality
  - All public APIs must have comprehensive integration tests
  - All error handling paths must be explicitly tested

## Success Criteria
The implementation will be considered successful when it demonstrably:

1. Maintains impenetrable information boundaries between client engagements while enabling appropriate pattern recognition
2. Accurately tracks framework effectiveness across different industries and provides relevant recommendations
3. Captures comprehensive engagement learnings in a structured, searchable format
4. Identifies relevant past insights for new situations while respecting confidentiality constraints
5. Generates fully anonymized case studies and teaching materials from client-specific experiences
6. Performs efficiently with large collections of consulting knowledge spanning numerous engagements
7. Preserves all data in accessible formats that ensure long-term availability
8. Passes all specified tests with the required code coverage metrics

To set up the development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install required dependencies
uv sync
```