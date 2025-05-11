# ConsultantBrain - A Knowledge Management System for Strategic Consultants

## Overview
ConsultantBrain is a specialized knowledge management system designed for strategic consultants who need to organize insights across different industries, preserve client confidentiality, track the effectiveness of business frameworks, capture lessons from engagements, and recognize patterns applicable to new situations. The system enables consultants to leverage past experience while maintaining strict ethical boundaries between client engagements.

## Persona Description
Elena advises businesses across different industries, drawing connections between previous client experiences, market research, and emerging trends. She needs to leverage past insights for new client situations while maintaining strict confidentiality between engagements.

## Key Requirements
1. **Client information firewall** - Implement a robust system for preserving confidentiality while enabling pattern recognition across engagements. This capability is critical for Elena to maintain strict ethical boundaries between clients, fulfill confidentiality obligations while still learning from past experiences, and extract generalizable insights without revealing specific client details. The system must enforce information compartmentalization while supporting cross-engagement learning.

2. **Industry framework application tracking** - Create a comprehensive mechanism for documenting which business models and analytical frameworks are most effective in different industry contexts. This feature allows Elena to build an evidence base for framework selection, refine her approach based on past successes and failures, and quickly identify relevant tools for new client situations. The tracking must support detailed context recording and outcome measurement for framework applications.

3. **Engagement retrospective** - Develop a structured system for capturing lessons learned from project outcomes. This functionality helps Elena continuously improve her consulting methodology, document what worked and what didn't in specific situations, and build an organized knowledge base of consulting experiences. The retrospective framework should support both factual outcome documentation and reflective analysis of the consulting process.

4. **Pattern recognition** - Implement intelligent tools for suggesting relevant past insights that may apply to new client situations. This capability enables Elena to recognize similarities between seemingly different business challenges, leverage her accumulated expertise effectively, and provide clients with proven approaches tailored to their specific context. The system must identify meaningful patterns while accounting for critical differences between situations.

5. **Anonymized case study generation** - Create mechanisms for sharing knowledge without revealing confidential sources. This feature allows Elena to develop teaching materials from real experiences, communicate her expertise effectively to potential clients, and contribute to professional knowledge sharing while protecting client privacy. The anonymization must be systematic enough to prevent identification of source organizations while preserving the valuable insights.

## Technical Requirements
- **Testability Requirements**:
  - All functionality must be implemented through well-defined APIs
  - Confidentiality mechanisms must be verifiable with information isolation tests
  - Framework tracking must support outcome validation against defined metrics
  - Retrospective systems must maintain structural and referential integrity
  - Pattern matching algorithms must produce consistent, replicable results
  - Anonymization effectiveness must be objectively measurable

- **Performance Expectations**:
  - System must efficiently handle repositories with 1,000+ client engagements
  - Information firewall operations must complete verification in under 1 second
  - Framework application queries must return results in under 2 seconds across the knowledge base
  - Pattern recognition must process 10,000+ potential matches in under 5 seconds
  - Anonymization procedures must process detailed case studies in under 3 seconds

- **Integration Points**:
  - Support for importing structured data from common business analysis tools
  - Export capabilities for anonymized case studies to portable formats
  - Integration framework for industry classification systems
  - Compatibility with standard business frameworks and methodologies
  - Support for secure, compartmentalized storage of client-specific information

- **Key Constraints**:
  - All data must be stored locally with strong isolation between confidential sections
  - No user interface components - all functionality exposed through APIs
  - Implementation must enforce strict information boundaries by design
  - System must support robust audit trails for confidentiality compliance
  - Access controls must be enforceable at the data element level

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
ConsultantBrain needs to implement these core capabilities:

1. **Confidentiality Management System**: A sophisticated framework for information isolation:
   - Client data compartmentalization with configurable boundary enforcement
   - Multi-level information classification by sensitivity
   - Controlled abstraction for creating non-confidential insights
   - Cross-client pattern extraction without specific detail leakage
   - Audit trails for all information barrier operations

2. **Framework Knowledge Base**: A system for business methodology management:
   - Framework definition with structured components and parameters
   - Context tagging for industry, company size, market conditions, etc.
   - Outcome tracking with success metrics and effectiveness ratings
   - Adaptation history showing how frameworks evolve through application
   - Suitability assessment for matching frameworks to new situations

3. **Engagement Intelligence Repository**: A comprehensive retrospective system:
   - Structured engagement documentation with standardized attributes
   - Outcome assessment with both quantitative and qualitative measures
   - Key learning extraction with categorization and priority rating
   - Success/failure factor identification with causal analysis
   - Cross-engagement comparison for methodology improvement

4. **Pattern Recognition Engine**: An advanced system for insight matching:
   - Similarity detection across diverse business scenarios
   - Attribute-based matching with configurable relevance weighting
   - Precedent retrieval with confidence scoring
   - Contextual adaptation suggestions for applying past insights
   - Pattern validation through outcome correlation analysis

5. **Knowledge Sharing Framework**: A system for secure insight distribution:
   - Anonymization protocols with configurable obfuscation levels
   - Identifying information detection and removal
   - Case study templating with standardized structures
   - Insight preservation during anonymization processes
   - Verification tools for confirming non-attributability

## Testing Requirements
The implementation must include comprehensive tests that verify all aspects of the system:

- **Key Functionalities to Verify**:
  - Client information firewall correctly maintains confidentiality while enabling pattern recognition
  - Industry framework tracking accurately documents effectiveness in different contexts
  - Engagement retrospectives properly capture lessons learned from project outcomes
  - Pattern recognition successfully identifies relevant past insights for new situations
  - Anonymized case studies effectively share knowledge without revealing sources

- **Critical User Scenarios**:
  - Adding new confidential client information with appropriate isolation
  - Recording the application and outcomes of a specific framework in an industry context
  - Documenting retrospective learnings from a completed client engagement
  - Identifying patterns from past engagements relevant to a new client scenario
  - Generating an anonymized case study from a sensitive client engagement

- **Performance Benchmarks**:
  - Information firewall must enforce boundaries across 1,000+ client records in real-time
  - Framework tracking must support at least 200 frameworks across 50+ industry contexts
  - Retrospective system must handle 500+ detailed engagement records with sub-second retrieval
  - Pattern recognition must evaluate 5,000+ potential matches in under 10 seconds
  - Anonymization must process a detailed 50-page case study in under 5 seconds

- **Edge Cases and Error Conditions**:
  - Handling attempted cross-client information access
  - Managing frameworks with contradictory effectiveness in similar contexts
  - Capturing learnings from engagements with ambiguous or mixed outcomes
  - Detecting false positive patterns with superficial similarities
  - Ensuring anonymization for highly unique or identifiable client situations

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for confidentiality enforcement mechanisms
  - 95% coverage for pattern recognition algorithms
  - 100% coverage for anonymization procedures
  - 95% branch coverage for framework effectiveness tracking

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
The implementation will be considered successful if it meets the following criteria:

1. Consultants can maintain strict client confidentiality while recognizing patterns across engagements
2. Business frameworks can be tracked for effectiveness across different industry contexts
3. Engagement outcomes and lessons learned are systematically captured for future reference
4. Relevant past insights can be identified and suggested for application to new client situations
5. Valuable consulting knowledge can be shared through properly anonymized case studies

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment:
1. Use `uv venv` to create a virtual environment
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL REMINDER: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```