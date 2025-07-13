# PyTemplate for Educational Content Generation

## Overview
A specialized template rendering engine for creating adaptive educational materials including quizzes, assignments, and interactive content that adjusts to different learning levels and ensures accessibility compliance.

## Persona Description
An educator creating interactive learning materials who needs templates for quizzes, assignments, and course content. He wants to generate different versions of materials for various learning levels.

## Key Requirements
1. **Question bank integration with randomization**: Connect to question databases and generate randomized quiz/test versions while maintaining difficulty balance and topic coverage. This is critical for creating fair assessments that prevent cheating while ensuring comprehensive evaluation.

2. **Difficulty-based content adaptation**: Automatically adjust content complexity, vocabulary, and examples based on target learning level (elementary, intermediate, advanced). This enables educators to create materials that meet students at their current understanding level.

3. **Interactive element generation (quizzes, exercises)**: Generate various interactive components including multiple choice questions, fill-in-the-blanks, matching exercises, and coding challenges. This is essential for engaging students and providing immediate practice opportunities.

4. **Learning path conditional rendering**: Create branching content that adapts based on student prerequisites, completed modules, or assessment results. This supports personalized learning experiences that guide students through appropriate content sequences.

5. **Accessibility compliance checking**: Ensure all generated content meets WCAG 2.1 AA standards with proper heading structure, alt text, and reading order. This is crucial for inclusive education that serves all learners regardless of abilities.

## Technical Requirements
- **Testability**: All content generation and adaptation logic must be testable via pytest
- **Performance**: Must handle large question banks (10,000+ items) and generate materials quickly
- **Integration**: Clean API for integration with Learning Management Systems and question databases
- **Key Constraints**: No UI components; must generate accessible content; support for multiple content formats

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The template engine must provide:
- Question bank interface with filtering by topic, difficulty, and type
- Randomization engine ensuring balanced assessment generation
- Content adaptation system with reading level analysis
- Interactive element generators for various exercise types
- Learning path resolver with prerequisite checking
- Accessibility validator with automated remediation suggestions
- Answer key generator with detailed explanations
- Rubric generator for subjective assessments

## Testing Requirements
All components must be thoroughly tested with pytest, including:
- **Question randomization tests**: Verify balanced selection across topics and difficulties
- **Content adaptation tests**: Validate appropriate adjustments for different levels
- **Interactive element tests**: Ensure correct generation of various exercise types
- **Learning path tests**: Verify correct conditional content selection
- **Accessibility tests**: Validate WCAG compliance for all generated content
- **Performance tests**: Benchmark handling of large question banks
- **Edge cases**: Handle missing questions, invalid difficulty levels, circular prerequisites
- **Format tests**: Verify output in multiple formats (HTML, Markdown, PDF-ready)

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
The implementation is successful when:
- Question randomization maintains topic balance and difficulty distribution
- Content adapts appropriately to three distinct learning levels
- Interactive elements generate correctly with proper answer validation
- Learning paths adjust based on prerequisites and progress
- All content passes WCAG 2.1 AA accessibility standards
- Large assessments (100+ questions) generate in under 5 seconds
- Generated materials integrate seamlessly with common LMS platforms
- All tests pass with comprehensive educational content validation

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions
1. Create a new virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in development mode with `uv pip install -e .`
4. Run tests with pytest-json-report to generate the required results file