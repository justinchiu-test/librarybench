# ResearchBrain

A specialized personal knowledge management system tailored for academic researchers who need to organize complex scientific literature, track research projects, and maintain structured connections between research notes, publications, and grant proposals.

## Features

- **Citation-aware note linking**: Automatically connect notes to referenced academic papers
- **Research question tracking**: Map research hypotheses to supporting and contradicting evidence
- **Grant proposal workspaces**: Organize knowledge for funding applications
- **Experiment logging templates**: Structured metadata templates for scientific reproducibility
- **Collaborative annotation importing**: Import and integrate feedback from colleagues

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/researchbrain.git
cd researchbrain

# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
uv sync
```

## Usage

```python
from researchbrain.core import ResearchBrain

# Initialize the system
rb = ResearchBrain(storage_path="./research_data")

# Import papers
paper_id = rb.import_paper("path/to/paper.pdf")

# Create notes with citations
note_id = rb.create_note(
    title="Thoughts on neuroplasticity",
    content="Recent studies show that neuroplasticity extends into adulthood [@smith2023].",
    tags=["neuroplasticity", "brain-development"]
)

# Link notes to papers
rb.link_note_to_paper(note_id, paper_id, page=42)

# Create research questions
question_id = rb.create_research_question(
    question="How does sleep affect memory consolidation?",
    description="Investigating the role of different sleep phases in memory formation."
)

# Add evidence to research questions
rb.add_evidence_to_question(
    question_id=question_id,
    note_id=note_id,
    strength="strong",
    type="supporting"
)
```

## Testing

ResearchBrain includes comprehensive test coverage for all core functionality:

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/test_citation_accuracy.py
uv run pytest tests/test_bidirectional_linking.py
uv run pytest tests/test_research_questions.py
uv run pytest tests/test_experiment_templates.py
uv run pytest tests/test_grant_proposals.py
uv run pytest tests/test_collaboration.py

# Run performance tests (large-scale tests are skipped by default)
uv run pytest tests/test_performance_requirements.py

# Run performance tests including large-scale tests
RUN_LARGE_PERFORMANCE_TESTS=1 uv run pytest tests/test_performance_requirements.py
```

The test suite verifies the following critical requirements:

1. **Citation Parsing Accuracy**: Tests for accurate parsing and formatting of academic citations across multiple formats (APA, MLA, Chicago, etc.)
2. **Bidirectional Link Integrity**: Tests for proper bidirectional navigation between notes and source materials
3. **Research Question Mapping**: Tests for tracking research questions and their supporting/contradicting evidence
4. **Experiment Templates**: Tests for creating and using scientific experiment templates
5. **Grant Proposal Workspaces**: Tests for organizing and exporting grant proposal information
6. **Collaborative Annotations**: Tests for managing feedback from research collaborators
7. **Performance Requirements**: Tests for system performance with large data collections

## Development

```bash
# Run tests
uv run pytest

# Type checking
uv run pyright

# Linting and formatting
uv run ruff check .
uv run ruff format
```

## License

MIT