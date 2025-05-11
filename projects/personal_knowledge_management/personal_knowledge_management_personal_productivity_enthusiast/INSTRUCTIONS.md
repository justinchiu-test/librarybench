# GrowthBrain: Knowledge Management System for Personal Productivity Enthusiasts

## Overview
GrowthBrain is a specialized personal knowledge management system designed for productivity enthusiasts who need to extract actionable insights from diverse learning sources, align knowledge acquisition with personal values, track habit implementation, and transform information into an integrated personal development system.

## Persona Description
Marcus is committed to continuous personal improvement, collecting insights from books, podcasts, articles, and courses. He needs to integrate diverse learning inputs into an actionable personal development system.

## Key Requirements
1. **Actionable insight extraction**: Identify and capture key takeaways from various learning materials, transforming passive content consumption into concrete action steps. This capability is essential for converting theoretical knowledge into practical application, preventing the accumulation of unused information, and ensuring learning leads to actual behavior change and improvement.

2. **Habit tracking**: Connect knowledge acquisition with behavior implementation by linking insights to specific habit formation plans and tracking progress over time. This feature helps bridge the gap between knowledge and action, creates accountability for applying what's been learned, and provides data on which insights actually translate into sustainable behavior change.

3. **Personal values alignment**: Categorize and organize information according to life priority areas, ensuring learning activities support core personal values and goals. This value-based organization helps prevent scattered knowledge acquisition, ensures learning efforts align with what truly matters to Marcus, and creates a coherent personal development strategy rather than disconnected improvement efforts.

4. **Learning source comparison**: Analyze where different authorities agree or conflict on key topics, developing nuanced understanding and identifying consensus. This comparative approach helps evaluate the reliability of different information sources, develop critical thinking about contradictory advice, and synthesize diverse perspectives into a coherent personal philosophy.

5. **Progressive summarization**: Distill lengthy materials into increasingly condensed forms, creating layers of abstraction for efficient future reference. This distillation process preserves the essence of valuable information while reducing cognitive overhead, enables quick review of previously processed material, and creates a personal knowledge base optimized for both retention and retrieval.

## Technical Requirements
- **Testability requirements**:
  - Insight extraction methods must be verifiable for quality and actionability
  - Habit tracking must be validated for accurate progress measurement
  - Values alignment categorization must be testable against defined personal priorities
  - Source comparison must be verifiable for accurate representation of different viewpoints
  - Progressive summarization must be testable for information preservation at different levels

- **Performance expectations**:
  - System must efficiently handle 1,000+ knowledge sources and 10,000+ individual notes
  - Insight extraction should process a typical book summary in under 30 seconds
  - Habit tracking should support at least 50 concurrent habits with daily data points
  - Full-text search across all personal knowledge should return results in under 2 seconds
  - Progressive summarization should generate multiple abstraction levels in under 5 seconds

- **Integration points**:
  - Plain text and Markdown file support
  - Import capabilities for different content formats
  - Habit data tracking and visualization
  - Personal values framework definition
  - Spaced repetition for knowledge review

- **Key constraints**:
  - All data must be stored locally in accessible, plain-text formats
  - No dependency on external web services for core functionality
  - Must support offline operation
  - Must be usable with minimal setup and configuration
  - Must maintain perfect reliability for habit tracking and personal metrics

## Core Functionality
The system must implement a comprehensive knowledge management foundation with specialized features for personal development:

1. **Knowledge Acquisition and Processing**:
   - Import and process content from diverse learning sources
   - Extract key insights and actionable takeaways
   - Categorize information by topic, source, and application area
   - Implement progressive summarization for layered abstraction

2. **Action and Implementation Framework**:
   - Convert insights into specific action steps
   - Link knowledge items to habit formation plans
   - Track habit implementation and consistency
   - Measure the practical impact of applied knowledge

3. **Personal Development Organization**:
   - Define and maintain a personal values framework
   - Align knowledge acquisition with priority life areas
   - Balance development across different domains
   - Assess knowledge gaps in important areas

4. **Critical Thinking and Synthesis**:
   - Compare perspectives from different sources on the same topics
   - Identify areas of expert consensus and disagreement
   - Develop nuanced understanding of complex subjects
   - Create personal position statements on key topics

5. **Review and Retention System**:
   - Implement spaced repetition for key insights
   - Create layered summarization for efficient review
   - Track knowledge application and results
   - Maintain long-term knowledge accessibility

## Testing Requirements
The implementation must be thoroughly testable with comprehensive pytest coverage:

- **Key functionalities that must be verified**:
  - Insight extraction correctly identifies actionable takeaways from learning materials
  - Habit tracking accurately records implementation consistency and progress
  - Values alignment properly categorizes information according to personal priorities
  - Learning source comparison correctly identifies agreements and conflicts between sources
  - Progressive summarization preserves essential information through multiple abstraction levels

- **Critical user scenarios that should be tested**:
  - Processing learning materials from different sources and extracting actionable insights
  - Converting knowledge into habits and tracking implementation over time
  - Organizing knowledge acquisition according to personal values and priorities
  - Comparing conflicting advice from different sources to develop a nuanced perspective
  - Creating progressive summarizations of important content for efficient future reference

- **Performance benchmarks that must be met**:
  - Sub-second response time for most knowledge retrieval operations
  - Efficient handling of 10,000+ knowledge items
  - Responsive habit tracking with daily data points
  - Memory-efficient operation suitable for standard laptop environments

- **Edge cases and error conditions that must be handled properly**:
  - Contradictory advice from equally credible sources
  - Habits with complex implementation patterns or criteria
  - Values conflicts requiring prioritization decisions
  - Very lengthy source materials requiring multi-level summarization
  - Incomplete or abandoned learning projects

- **Required test coverage metrics**:
  - Minimum 90% code coverage across all core modules
  - 100% coverage of habit tracking and values alignment functionality
  - All public APIs must have comprehensive integration tests
  - All error handling paths must be explicitly tested

## Success Criteria
The implementation will be considered successful when it demonstrably:

1. Effectively extracts actionable insights from diverse learning materials with clear implementation paths
2. Creates reliable habit tracking that connects knowledge acquisition with behavior change
3. Organizes personal knowledge according to a coherent framework of personal values and priorities
4. Provides clear comparison of different perspectives on the same topics, highlighting agreements and conflicts
5. Implements progressive summarization that preserves essential information while creating efficient review layers
6. Performs efficiently with large personal knowledge collections containing thousands of items
7. Preserves all data in accessible formats that ensure long-term availability
8. Passes all specified tests with the required code coverage metrics

To set up the development environment:
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install required dependencies
uv pip install -e .
```