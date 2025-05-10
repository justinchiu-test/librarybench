# Narrative Analysis Toolkit

## Overview
A specialized natural language processing toolkit designed for fiction writers to track character voices, analyze narrative consistency, identify perspective shifts, visualize story pacing, and monitor thematic elements across manuscripts.

## Persona Description
Priya is a novelist working on character development and narrative consistency across a series of books. She needs linguistic analysis tools to track character voices, plot elements, and thematic consistency throughout her manuscripts.

## Key Requirements
1. **Character Voice Consistency**: Develop algorithms to identify and measure distinctive speech patterns, vocabulary choices, phrase structures, and linguistic quirks of individual characters across different scenes and chapters. This is crucial for ensuring believable character development and preventing accidental voice blending that confuses readers and weakens characterization.

2. **Point-of-View Analysis**: Create analysis capabilities to detect perspective shifts, narrative distance changes, and focalization inconsistencies throughout a manuscript, helping maintain intended viewpoint discipline. This helps writers maintain consistent narrative perspective, avoiding unintentional head-hopping or perspective slips that disrupt reader immersion.

3. **Show-Don't-Tell Identification**: Implement pattern recognition to highlight passages of expository telling that could be converted to more engaging showing through dialogue, action, or sensory detail. This addresses one of the most common craft issues in fiction writing by identifying opportunities to transform abstract statements into concrete scenes that strengthen reader engagement.

4. **Pacing Visualization**: Develop analytical frameworks to map emotional intensity, action dynamics, exposition density, and narrative time-dilation throughout story arcs, helping balance and rhythm. This provides objective insight into story rhythm and tempo, allowing writers to identify and correct pacing problems like saggy middles or rushed climaxes.

5. **Thematic Word Cloud Generation**: Create statistical analysis tools to track symbolic language, recurring motifs, and thematic elements across a manuscript, visualizing their distribution and evolution. This helps writers reinforce important themes with appropriate consistency and development, ensuring key motifs receive proper emphasis and closure.

## Technical Requirements
- **Testability Requirements**:
  - All analysis algorithms must produce consistent, deterministic results
  - Character voice metrics must be quantifiable and comparable
  - POV detection must identify known perspective shifts
  - Show/tell classification must align with craft best practices
  - Thematic tracking must identify recurring motifs reliably

- **Performance Expectations**:
  - Process novel-length manuscripts (100K+ words) efficiently
  - Support incremental analysis for newly written sections
  - Handle series-spanning analysis for multi-book projects
  - Generate visualizations and reports in reasonable timeframes
  - Maintain responsive performance during manuscript editing

- **Integration Points**:
  - Support for common manuscript formats (DOCX, TXT, RTF, etc.)
  - Export capabilities for analysis results in useful formats
  - Character and theme definition persistence between sessions
  - Processing of narrative-specific structural elements
  - Support for custom dictionaries and style preferences

- **Key Constraints**:
  - Use only Python standard library without external dependencies
  - Focus on fiction-specific linguistic patterns and structures
  - Adapt to different fiction genres with distinct conventions
  - Preserve creative flexibility while providing useful metrics
  - Balance technical analysis with craft-oriented feedback

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement:

1. Character linguistic profiling:
   - Distinctive vocabulary and phrase extraction
   - Sentence structure and rhythm analysis
   - Dialogue attribution pattern recognition
   - Character-specific linguistic marker tracking
   - Voice consistency measurement across scenes

2. Narrative perspective analysis:
   - Point-of-view classification (first, close third, omniscient, etc.)
   - Perspective shift detection and boundary identification
   - Filter words and psychic distance measurement
   - Character knowledge boundary monitoring
   - Focalization consistency verification

3. Fiction-specific stylistic analysis:
   - Show vs. tell classification with context awareness
   - Sensory detail and abstract statement recognition
   - Filtering and distancing language identification
   - Passive construction and adverb usage analysis
   - Dialogue and action-to-exposition ratio calculation

4. Narrative rhythm and pacing frameworks:
   - Scene and sequel structure identification
   - Tension and conflict intensity estimation
   - Narrative time compression/dilation detection
   - Action and reflection density mapping
   - Emotional valence tracking throughout arcs

5. Thematic and symbolic tracking:
   - Motif and symbol identification across text
   - Thematic language cluster detection
   - Word family and conceptual grouping
   - Image pattern evolution throughout narrative
   - Frequency and distribution visualization

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accuracy of character voice differentiation metrics
  - Precision of point-of-view shift detection
  - Reliability of show vs. tell classification
  - Effectiveness of pacing analysis visualization
  - Completeness of thematic element tracking

- **Critical User Scenarios**:
  - Analyzing voice consistency for a character across a manuscript
  - Detecting unintended POV shifts in specific chapters
  - Identifying exposition-heavy sections needing dramatization
  - Visualizing the emotional arc and pacing of a complete novel
  - Tracking the development of a specific theme or motif

- **Performance Benchmarks**:
  - Process 100,000-word manuscripts in under 5 minutes
  - Generate character voice profiles with at least 20 distinctive features
  - Identify POV shifts with 90%+ accuracy compared to manual review
  - Create useful pacing visualizations for full-length novels
  - Track at least 50 simultaneous thematic elements across a manuscript

- **Edge Cases and Error Conditions**:
  - Handling unreliable narrator techniques
  - Processing experimental narrative structures
  - Managing nested narrative frames and stories-within-stories
  - Analyzing dialogue-heavy or unusual formatting
  - Accommodating genre-specific conventions and styles

- **Required Test Coverage**:
  - 90%+ coverage of all analysis algorithms
  - Comprehensive testing with diverse fiction genres
  - Validation against professionally edited manuscripts
  - Testing with known craft issues and their corrections
  - Verification of thematic tracking with annotated texts

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful when:

1. Character voice analysis provides actionable insights for maintaining distinct character voices
2. Point-of-view analysis correctly identifies perspective inconsistencies requiring attention
3. Show-don't-tell identification helps transform telling passages into more engaging scenes
4. Pacing visualization reveals meaningful patterns that correspond to reader experience
5. Thematic tracking successfully identifies recurring motifs and their distribution
6. The toolkit processes novel-length manuscripts with acceptable performance
7. Analysis results provide craft-relevant feedback rather than just technical metrics
8. Writers can effectively use the analysis to strengthen narrative consistency
9. The system accommodates different fiction genres and stylistic approaches
10. Analysis supports multi-book consistency for series projects

## Development Environment
To set up the development environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.