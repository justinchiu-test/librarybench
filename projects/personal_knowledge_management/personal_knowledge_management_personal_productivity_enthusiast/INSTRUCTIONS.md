# GrowthBank - A Knowledge Management System for Personal Productivity

## Overview
GrowthBank is a specialized knowledge management system designed for personal development enthusiasts who need to organize insights from diverse learning materials and transform them into actionable knowledge. The system helps users extract key takeaways, track habit implementation, align knowledge with personal values, compare different learning sources, and distill extensive materials into increasingly refined summaries.

## Persona Description
Marcus is committed to continuous personal improvement, collecting insights from books, podcasts, articles, and courses. He needs to integrate diverse learning inputs into an actionable personal development system.

## Key Requirements
1. **Actionable insight extraction** - Develop a robust framework for identifying, categorizing, and retrieving key takeaways from various learning materials. This capability is essential for Marcus to transform passive content consumption into practical wisdom, distill the most valuable concepts from each learning resource, and build an organized repository of applicable insights. The system must support different insight types (principles, techniques, mental models, etc.) and maintain connections to their original contexts.

2. **Habit tracking** - Create a system that connects knowledge acquisition with behavior implementation through habit formation tracking. This feature allows Marcus to bridge the gap between theoretical understanding and practical application, monitor his progress in applying new concepts in daily life, and identify which knowledge areas are successfully translating into behavioral change. The tracking should support various habit formation models and implementation timeframes.

3. **Personal values alignment** - Implement a mechanism for categorizing information by life priority areas and personal values. This functionality helps Marcus ensure that his learning efforts support his core values and life goals, identify knowledge gaps in priority areas, and make intentional decisions about which concepts to implement. The system should support personalized value hierarchies and flexible categorization schemes that evolve over time.

4. **Learning source comparison** - Design tools for analyzing where different authorities agree or conflict on specific topics or recommendations. This capability enables Marcus to develop nuanced understanding through triangulation of multiple perspectives, identify consensus patterns across diverse sources, and make informed decisions when facing contradictory advice. The comparison framework should highlight both similarities and meaningful differences between sources.

5. **Progressive summarization** - Create a methodology for distilling lengthy materials into increasingly condensed forms through multiple refinement passes. This feature helps Marcus internalize complex concepts through active processing, create layers of abstraction for efficient future reference, and develop increasingly powerful mental models through iterative refinement. The system should support multiple summarization layers while maintaining links to the original comprehensive material.

## Technical Requirements
- **Testability Requirements**:
  - All functionality must be implemented through well-defined APIs
  - Insight extraction algorithms must be testable with standardized learning materials
  - Habit tracking must support verification against predefined behavior patterns
  - Values alignment must be testable with configurable value hierarchies
  - Source comparison algorithms must produce consistent, verifiable results
  - Summarization quality must be objectively measurable

- **Performance Expectations**:
  - System must efficiently handle knowledge bases with 10,000+ notes and insights
  - Full-text search must return results in under 1 second across the entire knowledge base
  - Habit tracking analysis must process 1,000+ data points in under 3 seconds
  - Source comparison must handle analyses across 100+ references in under 5 seconds
  - Progressive summarization operations must process lengthy documents in under 2 seconds

- **Integration Points**:
  - Support for importing content from common formats (PDF, EPUB, MP3, etc.)
  - Export capabilities for insights and summaries to portable formats
  - Integration with time tracking and calendar data for habit correlation
  - Support for extracting structured data from various learning platforms
  - Compatibility with spaced repetition systems for insight reinforcement

- **Key Constraints**:
  - All data must be stored locally without cloud dependencies
  - No user interface components - all functionality exposed through APIs only
  - Implementation must be cross-platform compatible
  - System must operate efficiently with limited memory resources
  - Support for incremental processing of large learning materials

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
GrowthBank needs to implement these core capabilities:

1. **Insight Management System**: A comprehensive framework for knowledge extraction and organization:
   - Insight identification algorithms with multiple extraction strategies
   - Classification framework for different insight types
   - Contextual linking between insights and source materials
   - Relevance scoring for practical applicability
   - Search and retrieval optimized for actionability

2. **Habit Development Framework**: A system connecting knowledge to behavior:
   - Habit definition with configurable tracking parameters
   - Implementation monitoring with streak and consistency metrics
   - Knowledge-to-behavior linkage tracking
   - Progress visualization using text-based formats
   - Accountability mechanisms with reflection prompts

3. **Personal Values Framework**: A system for aligning learning with priorities:
   - Flexible value hierarchy definition
   - Multi-dimensional categorization of insights by values
   - Gap analysis between values and accumulated knowledge
   - Priority scoring for competing learning directions
   - Value alignment assessment for potential habits

4. **Source Analysis Engine**: A framework for comparative learning:
   - Thematic mapping across different learning sources
   - Agreement/disagreement detection algorithms
   - Authority weighting based on configurable criteria
   - Consensus identification across multiple sources
   - Contradiction flagging with context preservation

5. **Progressive Refinement System**: A methodology for multi-layer summarization:
   - Layer-based summarization with configurable compression ratios
   - Key point extraction with importance ranking
   - Cross-reference maintenance between summary layers
   - Quality metrics for summarization effectiveness
   - Incremental refinement capabilities for ongoing improvement

## Testing Requirements
The implementation must include comprehensive tests that verify all aspects of the system:

- **Key Functionalities to Verify**:
  - Actionable insight extraction correctly identifies and categorizes key takeaways
  - Habit tracking properly connects knowledge concepts with behavior implementation
  - Personal values alignment accurately categorizes information by priority areas
  - Learning source comparison effectively identifies agreements and conflicts
  - Progressive summarization successfully distills materials into increasingly refined forms

- **Critical User Scenarios**:
  - Extracting actionable insights from a complex book on personal effectiveness
  - Tracking the implementation of a new productivity technique learned from a course
  - Categorizing a collection of health-related content according to personal wellness values
  - Comparing contradictory advice from three different sources on the same topic
  - Progressively summarizing a lengthy article through three layers of refinement

- **Performance Benchmarks**:
  - Insight extraction must process a 300-page book equivalent in under 30 seconds
  - Habit tracking must analyze 365 days of implementation data in under 5 seconds
  - Values alignment must categorize 1,000+ insights across 20+ value areas in under 10 seconds
  - Source comparison must analyze 50+ sources on a single topic in under 8 seconds
  - Progressive summarization must process a 10,000-word document through 3 layers in under 5 seconds

- **Edge Cases and Error Conditions**:
  - Handling learning materials with minimal actionable content
  - Managing irregular or interrupted habit tracking data
  - Dealing with evolving personal values and re-categorization needs
  - Processing sources with highly technical or domain-specific language
  - Managing extremely lengthy or complex materials for summarization

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all core modules
  - 100% coverage for insight extraction algorithms
  - 95% coverage for habit tracking logic
  - 95% branch coverage for source comparison functions
  - 100% coverage for progressive summarization methods

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

1. Users can extract, categorize, and retrieve actionable insights from diverse learning materials
2. Knowledge can be connected to behavior implementation through habit tracking mechanisms
3. Information can be organized according to personalized value hierarchies and priority areas
4. Multiple learning sources can be compared to identify agreements and conflicts on specific topics
5. Lengthy materials can be progressively summarized into increasingly refined layers

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