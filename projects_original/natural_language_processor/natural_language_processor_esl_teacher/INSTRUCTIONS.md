# Language Learning Text Analysis Toolkit

A specialized natural language processing framework for analyzing text difficulty, identifying challenging vocabulary, and generating learning materials for English language learners at different proficiency levels.

## Overview

This project provides ESL (English as a Second Language) teachers with powerful tools to assess reading material difficulty, map texts to appropriate language proficiency levels, identify challenging vocabulary, detect cultural references requiring explanation, and automatically generate appropriate learning exercises. All functionality is implemented as Python libraries requiring no advanced programming knowledge.

## Persona Description

Carlos develops instructional materials for non-native English speakers and needs tools to assess reading difficulty, identify challenging vocabulary, and create level-appropriate learning exercises tailored to different language proficiency levels.

## Key Requirements

1. **Readability Analysis Engine**: Develop a comprehensive system for assessing text complexity with granular feedback on specific linguistic factors affecting readability.
   - This feature is essential for Carlos as it allows him to quickly evaluate whether texts are appropriate for specific learner levels and identify exactly which aspects make a text challenging.
   - The analysis must go beyond simple metrics like Flesch-Kincaid to identify specific syntactic structures, rare vocabulary, idiomatic expressions, and other elements that impact comprehension for non-native speakers.

2. **Language Proficiency Mapping Framework**: Create a system that classifies texts according to established language acquisition frameworks (such as CEFR, ACTFL, or other ESL standards).
   - This capability ensures Carlos can confidently select materials that align precisely with curriculum standards and learner abilities across different proficiency stages.
   - The framework must detect and quantify features that distinguish between adjacent proficiency levels (A1/A2, B1/B2, etc.) with high accuracy.

3. **Vocabulary Grading and Substitution System**: Implement tools to identify words outside a targeted learning level and suggest appropriate alternatives while maintaining text meaning.
   - This feature allows Carlos to efficiently adapt authentic materials to be accessible for learners without manually reviewing every word, saving significant preparation time.
   - The system must recognize context-dependent word difficulty, academic vocabulary, and specialized terminology to make appropriate recommendations.

4. **Cultural Reference Detector**: Build an algorithm to highlight culturally-specific idioms, expressions, and references that would require special explanation for non-native speakers.
   - This is critical for Carlos since cultural literacy gaps often cause greater comprehension difficulties than language itself, especially for intermediate and advanced learners.
   - The detector must identify subtle cultural references, idioms, slang, and expressions that might be transparent to native speakers but opaque to language learners.

5. **Exercise Generation Engine**: Develop a framework for automatically creating pedagogically sound language learning exercises from any text, including cloze tests, vocabulary practice, and comprehension questions.
   - This capability dramatically reduces Carlos's preparation time while ensuring consistent quality across learning materials targeted at different proficiency levels.
   - The system must generate exercises that test appropriate skills for each proficiency level, with distractors and answer keys that follow educational best practices.

## Technical Requirements

### Testability Requirements
- All readability metrics must be deterministic and yield consistent scores for the same text
- Proficiency level mapping must be verifiable against expert-classified sample texts
- Vocabulary grading must be testable against established ESL word lists for different levels
- Cultural reference detection must identify a high percentage of known idioms and expressions
- Generated exercises must follow established ESL pedagogical patterns and best practices

### Performance Expectations
- Process and analyze texts up to 10,000 words in under 5 seconds
- Generate comprehensive exercise sets for a 1,000-word text in under 10 seconds
- Handle batch processing of multiple texts (e.g., an entire textbook) efficiently
- Support incremental analysis to avoid reprocessing when making minor text changes
- Operate with minimal memory footprint suitable for standard laptop hardware

### Integration Points
- Accept plain text, Word documents, PDF, and HTML as input formats
- Provide programmatic access to all analysis results for integration with authoring tools
- Export exercises in standard formats (plain text, markdown, or structured JSON)
- Support integration of custom vocabulary lists and proficiency definitions
- Enable extensibility through custom rule sets for different language teaching approaches

### Key Constraints
- Implementation must use only Python standard library
- All algorithms must operate without requiring internet connectivity
- System must handle texts with mixed language proficiency levels in different sections
- Analysis must work effectively on both fiction and non-fiction content
- All components must be efficient enough for interactive use during lesson preparation
- Vocabulary and cultural references must be adaptable to different English varieties (US, UK, etc.)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system consists of five main components:

1. **Readability Analyzer**: A comprehensive text assessment engine that evaluates multiple dimensions of language complexity. It should:
   - Calculate standard readability metrics (Flesch-Kincaid, SMOG, etc.)
   - Identify complex syntactic structures (embedded clauses, passive voice, etc.)
   - Analyze vocabulary complexity beyond frequency (abstract terms, polysemy, etc.)
   - Evaluate text cohesion and discourse structure
   - Generate specific feedback on factors affecting comprehension difficulty

2. **Proficiency Level Mapper**: A framework for classifying texts according to language learning standards. It should:
   - Map texts to CEFR levels (A1-C2) based on linguistic features
   - Identify features that place text between defined levels
   - Compare text characteristics to level descriptors in official frameworks
   - Recommend specific adaptations to target different proficiency levels
   - Support customization for different curriculum standards

3. **Vocabulary Analyzer and Adaptation Tool**: A system for vocabulary assessment and text simplification. It should:
   - Identify words beyond targeted proficiency level
   - Suggest appropriate synonyms based on proficiency targets
   - Recognize context-dependent word difficulty
   - Flag technical or specialized vocabulary for glossary inclusion
   - Support academic word list integration for EAP (English for Academic Purposes)

4. **Cultural Reference Identifier**: A tool for detecting expressions requiring cultural literacy. It should:
   - Identify idioms, expressions, and phrasal verbs
   - Detect culturally-specific references (historical, literary, pop culture)
   - Flag humor, irony, and other pragmatic elements
   - Recognize political, religious, and social references
   - Categorize references by domain and expected familiarity

5. **Language Exercise Generator**: A framework for creating pedagogical materials. It should:
   - Generate cloze (fill-in-the-blank) exercises targeting specific skills
   - Create vocabulary practice activities appropriate to proficiency level
   - Produce comprehension questions at different cognitive levels
   - Develop grammar exercises based on text structures
   - Generate appropriate distractors and answer keys

## Testing Requirements

### Key Functionalities to Verify

1. Readability Analysis:
   - Test accuracy of standard readability metrics against reference implementations
   - Verify identification of complex syntactic structures
   - Test detection of vocabulary beyond specified proficiency levels
   - Validate consistency of scoring across similar texts
   - Verify detailed feedback generation for specific complexity factors

2. Proficiency Level Mapping:
   - Test classification accuracy against expert-labeled texts for each CEFR level
   - Verify feature detection that distinguishes between adjacent levels
   - Test adaptation recommendations for different target levels
   - Validate handling of texts with mixed-level features
   - Verify alignment with official CEFR descriptors

3. Vocabulary Grading:
   - Test identification accuracy against established ESL word lists
   - Verify context-appropriate synonym suggestions
   - Test handling of polysemous words and specialized terminology
   - Validate academic vocabulary identification
   - Verify preservation of meaning in simplified text versions

4. Cultural Reference Detection:
   - Test identification of common idioms and expressions
   - Verify recognition of cultural references across different domains
   - Test detection of humor, irony, and pragmatic elements
   - Validate categorization of references by type
   - Verify performance across different English varieties

5. Exercise Generation:
   - Test pedagogical soundness of generated exercises
   - Verify appropriate targeting of different proficiency levels
   - Test quality of generated distractors and answer keys
   - Validate variety and relevance of generated questions
   - Verify alignment with ESL teaching best practices

### Critical User Scenarios

1. Analyzing a news article to determine its appropriateness for intermediate (B1) learners
2. Adapting an authentic text by simplifying vocabulary while maintaining core meaning
3. Creating a comprehensive worksheet with exercises for a short story
4. Identifying cultural references in a text that require additional explanation
5. Developing a sequence of readings with gradually increasing difficulty levels

### Performance Benchmarks

- Process and analyze a 1,000-word text in under 2 seconds
- Complete vocabulary grading and suggest alternatives within 3 seconds for texts up to 2,000 words
- Generate a full exercise set including at least 5 different exercise types in under 5 seconds
- Identify at least 90% of cultural references present in test texts
- Achieve at least 85% agreement with expert ESL teachers on proficiency level classification

### Edge Cases and Error Conditions

- Test with texts containing specialized terminology or jargon
- Verify behavior with texts containing non-standard English or deliberate errors
- Test with content containing mixed languages or code-switching
- Validate performance with very short or very long texts
- Test with texts containing unusual formatting or structure
- Verify handling of culturally diverse content with multiple reference points
- Test with content specifically designed for language learners versus authentic texts

### Required Test Coverage Metrics

- Line coverage: Minimum 90%
- Branch coverage: Minimum 85%
- Function coverage: Minimum 95%
- All public APIs must have 100% test coverage
- All error handling paths must be tested
- All text processing algorithms must be thoroughly tested with diverse samples

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

- The readability analyzer correctly identifies at least 90% of complexity factors in test texts
- Proficiency level mapping agrees with expert ESL teacher assessment at least 85% of the time
- Vocabulary grading correctly identifies at least 90% of words beyond target proficiency levels
- Cultural reference detection identifies at least 85% of idioms and expressions in test content
- Generated exercises are rated as pedagogically appropriate by ESL experts

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up your development environment:

1. Create a virtual environment using uv:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. Install testing tools:
   ```
   pip install pytest pytest-json-report
   ```

5. Run tests with JSON reporting:
   ```
   pytest --json-report --json-report-file=pytest_results.json
   ```

IMPORTANT: Generating and providing the pytest_results.json file is a CRITICAL requirement for project completion. This file serves as proof that all tests pass and the implementation meets the specified requirements.