# Narrative Analysis Toolkit

A natural language processing library designed to analyze and enhance fiction writing through character voice tracking, narrative structure analysis, and thematic development tools.

## Overview

This project provides fiction writers with specialized text analysis capabilities focused on character voice consistency, narrative perspective, writing technique improvement, story pacing, and thematic development tracking. It enables authors to maintain consistency and improve craft across long-form narratives.

## Persona Description

Priya is a novelist working on character development and narrative consistency across a series of books. She needs linguistic analysis tools to track character voices, plot elements, and thematic consistency throughout her manuscripts.

## Key Requirements

1. **Character Voice Consistency**: Develop linguistic profiling to identify and track distinctive speech patterns, vocabulary preferences, and syntax habits for different characters across manuscript sections. This feature is critical for Priya because maintaining consistent and distinctive character voices across a novel or series is fundamental to characterization, and subtle inconsistencies that emerge during the writing process can weaken reader immersion.

2. **Point-of-View Analysis**: Create detection algorithms for narrative perspective shifts, identifying changes in viewpoint character, narrative distance (close vs. distant), and perspective (first/second/third person). This capability allows Priya to prevent unintentional POV slips that confuse readers, while also helping her intentionally craft effective perspective shifts when desired for narrative effect.

3. **Show-Don't-Tell Identification**: Implement pattern recognition for "telling" statements (direct exposition) versus "showing" narrative techniques, with recommendations for converting exposition to more engaging demonstrations. For Priya, improving this fundamental aspect of craft helps create more immersive fiction, transforming flat exposition into vivid scenes that engage readers more deeply.

4. **Pacing Visualization**: Build metrics to map emotional intensity, action, dialogue-to-narrative ratio, and scene length throughout the narrative arc, identifying potential pacing issues. This feature helps Priya identify and address structural problems like saggy middles, rushed climaxes, or imbalanced chapter pacing that could diminish reader engagement with her stories.

5. **Thematic Word Cloud Generation**: Create analysis tools to identify and track recurring symbolic language, motifs, and thematic vocabulary across manuscript sections. This capability enables Priya to ensure thematic consistency across a long work or series, strengthen intentional motifs, and identify unintentional repetition or thematic dilution.

## Technical Requirements

### Testability Requirements
- Character voice metrics must be consistent and objective across text samples
- POV detection must accurately identify perspective in diverse narrative styles
- Show/tell classification must correspond with established writing craft principles
- Pacing analysis must produce consistent results across similar structural patterns
- Thematic tracking must identify intentionally planted motifs with high precision

### Performance Expectations
- Process full novel manuscripts (80,000-120,000 words) in under 2 minutes
- Support comparison across multiple manuscript files
- Handle incremental analysis of manuscripts during writing process
- Memory usage suitable for running on standard author hardware
- Responsive analysis for interactive manuscript review

### Integration Points
- Standard manuscript format compatibility (DOCX, RTF, TXT, Markdown)
- Character and thematic data persistence between sessions
- Export capabilities for visualization and reporting
- Support for manuscript organization conventions (chapters, scenes, etc.)
- Optional integration with common author software file formats

### Key Constraints
- Implementation using only Python standard library (no external NLP dependencies)
- Analysis calibrated specifically for fiction and narrative text
- Features must accommodate different fiction genres and styles
- Processing must respect creative expression while providing objective metrics
- System must handle both structured and freeform narrative organization

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality required for this project includes:

1. **Character Linguistic Profiling**
   - Dialogue attribution and extraction
   - Vocabulary distinctiveness analysis
   - Syntactic pattern fingerprinting
   - Idiolect consistency tracking
   - Character-specific linguistic metrics

2. **Narrative Perspective Analysis**
   - POV classification and detection
   - Viewpoint character identification
   - Narrative distance measurement
   - Perspective shift detection
   - Free indirect discourse recognition

3. **Writing Technique Assessment**
   - Show vs. tell classification
   - Exposition identification
   - Sensory language measurement
   - Action/dialogue/description balance
   - Craft pattern recognition

4. **Narrative Structure Analysis**
   - Scene and chapter pacing metrics
   - Emotional intensity mapping
   - Action density tracking
   - Structural symmetry assessment
   - Arc and sequence identification

5. **Thematic Development Tracking**
   - Symbolic language identification
   - Motif recurrence analysis
   - Thematic vocabulary clustering
   - Concept frequency mapping
   - Thematic evolution tracking

## Testing Requirements

### Key Functionalities to Verify
- Accurate identification of character voice patterns with distinction between characters
- Correct detection of POV shifts and narrative perspective types
- Reliable classification of showing versus telling passages
- Precise mapping of narrative pacing elements throughout manuscript structure
- Valid extraction and tracking of thematic elements and motifs

### Critical User Scenarios
- Analyzing dialogue consistency for a character across a multi-book series
- Identifying unintentional POV shifts within a chapter
- Converting exposition-heavy passages to more engaging "shown" scenes
- Diagnosing pacing issues in a novel's middle sections
- Tracking the development of a key thematic motif across a manuscript

### Performance Benchmarks
- Complete character voice analysis for a 100,000-word novel in under 60 seconds
- POV classification with 90%+ accuracy against human-labeled samples
- Show/tell identification matching writing instructor assessment in 80%+ of cases
- Pacing visualization processing full manuscript in under 30 seconds
- Thematic tracking identifying planted motifs with precision exceeding 85%

### Edge Cases and Error Conditions
- Experimental or unconventional narrative styles
- Stream-of-consciousness and other complex POV techniques
- Genre-specific conventions and expectations
- Intentionally inconsistent character voices (for effect or character development)
- Nested narratives and frame stories
- Unreliable narrator techniques
- Multi-perspective narratives with frequent POV shifts

### Required Test Coverage Metrics
- 90% code coverage for character voice analysis components
- 95% coverage for POV detection algorithms
- 90% coverage for show/tell classification
- 90% coverage for pacing visualization tools
- 95% coverage for thematic tracking functions

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Character dialogue and narration patterns are consistently tracked with meaningful distinctiveness metrics
2. Point-of-view shifts are accurately detected with useful classification of narrative perspective
3. "Telling" passages are identified with actionable suggestions for conversion to "showing"
4. Narrative pacing is visualized with meaningful insights about structural balance
5. Thematic elements and motifs are tracked with useful frequency and distribution information
6. Performance meets specified benchmarks for full-length manuscripts
7. Analysis provides actionable insights that align with established writing craft principles
8. The system accommodates different fiction genres and narrative styles appropriately
9. Processing handles various manuscript organizational structures
10. The toolkit demonstrably helps authors improve narrative consistency and craft

## Getting Started

To set up the project:

1. Create a new library project:
   ```
   uv init --lib
   ```

2. Install development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a sample script:
   ```
   uv run python script.py
   ```