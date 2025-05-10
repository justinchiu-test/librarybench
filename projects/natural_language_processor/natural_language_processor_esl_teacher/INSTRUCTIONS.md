# Language Learning Text Processor

## Overview
A specialized natural language processing toolkit designed for ESL teachers to assess reading difficulty, identify challenging vocabulary, analyze linguistic features, and generate level-appropriate learning exercises for non-native English speakers at different proficiency levels.

## Persona Description
Carlos develops instructional materials for non-native English speakers and needs tools to assess reading difficulty, identify challenging vocabulary, and create level-appropriate learning exercises tailored to different language proficiency levels.

## Key Requirements
1. **Readability Scoring with Granular Feedback**: Implement comprehensive text analysis that goes beyond simplistic readability formulas, providing detailed feedback on specific complexity factors such as sentence structure, vocabulary difficulty, cohesion, and conceptual density. This allows teachers to understand exactly what makes a text challenging for language learners and where modifications might be needed.

2. **Language Acquisition Level Mapping**: Create a system to evaluate texts against established language proficiency frameworks (CEFR, ACTFL, etc.), matching content to appropriate learner levels (A1-C2) based on grammatical structures, vocabulary, and discourse features. This enables selection of texts that precisely match students' current proficiency levels for optimal comprehension and acquisition.

3. **Vocabulary Grading**: Develop algorithms to identify words outside targeted learning levels, highlighting terms that may require pre-teaching or substitution, with suggestions for level-appropriate alternatives. This helps teachers efficiently adapt authentic materials for different proficiency levels without manual word-by-word analysis.

4. **Cultural Reference Detection**: Implement pattern recognition to highlight culturally-specific idioms, expressions, references, and assumed knowledge that might require special explanation for non-native speakers. This addresses the cultural competence dimension of language learning that is often overlooked by standard readability measures.

5. **Exercise Generation**: Create a framework for automatically generating language learning activities from texts, including cloze tests (with strategic word removal based on learning objectives), vocabulary practice focusing on target words, and comprehension questions at appropriate cognitive levels. This dramatically reduces preparation time while ensuring exercises are pedagogically sound.

## Technical Requirements
- **Testability Requirements**:
  - All analysis algorithms must produce consistent, deterministic results
  - Readability evaluations must be validated against established ESL frameworks
  - Vocabulary identification must match standard level classifications
  - Exercise generation must follow sound pedagogical principles
  - All components must be independently testable with sample texts

- **Performance Expectations**:
  - Process typical teaching materials (articles, short stories) in seconds
  - Handle book-length texts for comprehensive analysis in under 5 minutes
  - Support batch processing of multiple texts for curriculum planning
  - Generate exercise sets rapidly for last-minute lesson preparation
  - Maintain reasonable memory usage with educational-scale texts

- **Integration Points**:
  - Import capabilities for common document formats (plain text, docx, pdf)
  - Export of analysis results and generated exercises in usable formats
  - Vocabulary checking against established word lists (GSL, AWL, etc.)
  - Support for custom vocabulary lists and proficiency definitions
  - Extensibility for additional languages beyond English

- **Key Constraints**:
  - Use only Python standard library without external dependencies
  - Design for language-teaching contexts with pedagogical validity
  - Support for explicit learning progression across proficiency levels
  - Focus on practical classroom and materials development use cases
  - Maintain accessibility for teachers without programming backgrounds

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement:

1. Comprehensive text analysis for language learning contexts:
   - Multi-factor readability assessment beyond formula-based scores
   - Grammatical structure complexity analysis
   - Vocabulary profiling against level-appropriate word lists
   - Discourse and cohesion feature identification
   - Cultural and background knowledge requirements

2. Proficiency level mapping frameworks:
   - Mapping texts to CEFR levels (A1-C2) based on multiple factors
   - Identifying features that place text at particular proficiency levels
   - Highlighting elements that cross proficiency boundaries
   - Suggesting modifications to adjust text to target levels
   - Visualizing proficiency level distribution within texts

3. Vocabulary processing specialized for language learning:
   - Frequency-based vocabulary identification
   - Academic and specialized vocabulary recognition
   - Idiom and collocation detection
   - Word family grouping and derivational relationships
   - Level-appropriate alternatives recommendation

4. Cultural and pragmatic content analysis:
   - Idiomatic expression identification
   - Cultural reference detection
   - Background knowledge assumption identification
   - Register and formality analysis
   - Pragmatic function recognition

5. Exercise generation frameworks for:
   - Cloze/gap-fill exercises with pedagogical targeting
   - Vocabulary practice activities at appropriate levels
   - Comprehension questions addressing different skills
   - Task difficulty calibration to proficiency levels
   - Answer key generation for teacher reference

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accuracy of readability analysis against expert ESL teacher evaluations
  - Precision of CEFR level mapping compared to standard exemplars
  - Reliability of vocabulary grading against established word lists
  - Effectiveness of cultural reference detection with diverse texts
  - Pedagogical validity of generated exercises

- **Critical User Scenarios**:
  - Evaluating authentic materials for classroom appropriateness
  - Adapting texts to specific proficiency level targets
  - Identifying vocabulary that requires pre-teaching
  - Generating supplementary exercises for reading assignments
  - Creating comprehensive lesson materials from source texts

- **Performance Benchmarks**:
  - Complete multi-factor analysis of 2,000-word texts in under 30 seconds
  - Generate complete exercise sets for standard texts in under 1 minute
  - Process curriculum-scale materials (20+ texts) in batch mode efficiently
  - Maintain consistent performance across text types and genres
  - Support reasonable processing times on standard teacher hardware

- **Edge Cases and Error Conditions**:
  - Handling poorly formatted or OCR-processed texts
  - Processing texts with mixed languages or code-switching
  - Managing specialized content with domain-specific vocabulary
  - Appropriately analyzing texts with non-standard English varieties
  - Graceful handling of extremely simple or complex outlier texts

- **Required Test Coverage**:
  - 90%+ coverage of all analysis algorithms
  - Comprehensive testing of exercise generation logic
  - Verification against established proficiency level exemplars
  - Validation with texts from diverse genres and domains
  - Testing across full range of proficiency levels (A1-C2)

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Readability analysis provides actionable insights beyond standard formulas, matching expert ESL teacher assessment
2. Texts are accurately mapped to appropriate CEFR or similar proficiency levels with clear rationale
3. Vocabulary is correctly identified by difficulty level with appropriate alternatives suggested
4. Cultural references and idioms are reliably detected across diverse text types
5. Generated exercises follow sound pedagogical principles and target appropriate skills
6. The system significantly reduces teacher preparation time for materials development
7. Analysis results provide clear guidance for text selection and adaptation
8. Exercise generation produces classroom-ready activities requiring minimal editing
9. All functionality maintains high accuracy across different text genres and proficiency levels

## Development Environment
To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.