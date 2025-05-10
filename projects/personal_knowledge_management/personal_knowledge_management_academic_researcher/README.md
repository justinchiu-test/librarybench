# Academic Research Knowledge Vault

A specialized personal knowledge management system tailored for academic researchers who need to organize complex scientific literature, experimental notes, and theoretical connections while preparing publications and grant proposals.

## Overview

Academic Research Knowledge Vault is a comprehensive knowledge management system designed to help academic researchers organize their research materials, streamline the process of organizing academic knowledge, and facilitate the discovery of new connections between research concepts.

The system provides powerful tools for:

- **Citation-aware note linking**: Automatically connect notes to referenced academic papers
- **Research question tracking**: Map hypotheses to supporting evidence and contradictions
- **Grant proposal workspaces**: Organize specific subsets of knowledge for funding applications
- **Experiment logging templates**: Create structured metadata for scientific reproducibility
- **Collaborative annotation importing**: Import colleague comments while maintaining personal knowledge structure

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/academic-knowledge-vault.git
cd academic-knowledge-vault

# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
uv sync
```

## Usage Examples

### Managing Notes with Citation Awareness

```python
from academic_knowledge_vault.storage.note_storage import NoteStorage
from academic_knowledge_vault.services.note_management.note_service import NoteService

# Initialize storage and service
note_storage = NoteStorage("/path/to/notes")
collection_storage = NoteCollectionStorage("/path/to/collections")
note_service = NoteService(note_storage, collection_storage)

# Create a note with citations
note_id = note_service.create_note(
    title="Neural Mechanisms of Memory Formation",
    content="""
    This paper by @smith2020 discusses the importance of sleep in memory consolidation.
    
    Another study [@jones2021] found contradictory evidence in older adults.
    """,
    tags=["memory", "neuroscience", "sleep"]
)

# The citation keys are automatically extracted
note = note_service.get_note(note_id)
print(note.citation_keys)  # Output: {'smith2020', 'jones2021'}
```

### Managing Research Questions and Evidence

```python
from academic_knowledge_vault.services.research_question.research_question_service import ResearchQuestionService

# Initialize the service
research_service = ResearchQuestionService(
    question_storage, hypothesis_storage, evidence_storage, collection_storage
)

# Create a research question
question_id = research_service.create_research_question(
    question="How does sleep quality affect memory consolidation in older adults?",
    knowledge_gaps=["Limited studies in older populations", "Mechanisms unclear"]
)

# Create a hypothesis
hypothesis_id = research_service.create_hypothesis(
    statement="Sleep quality decline in older adults leads to proportional decline in memory consolidation.",
    research_question_id=question_id
)

# Add supporting evidence
research_service.create_evidence(
    description="Study found strong correlation between slow-wave sleep and recall performance.",
    evidence_type="supporting",
    strength="strong",
    supports_ids=[hypothesis_id]
)

# Calculate evidence strength
strength = research_service.calculate_evidence_strength(hypothesis_id)
print(f"Evidence strength: {strength}")
```

### Managing Grant Proposals

```python
from academic_knowledge_vault.services.grant_proposal.grant_proposal_service import GrantProposalService

# Initialize the service
proposal_service = GrantProposalService(proposal_storage, workspace_storage)

# Create a workspace for a grant proposal
workspace_id = proposal_service.create_workspace(
    name="NIH Grant - Sleep and Memory in Aging",
    deadline=datetime(2023, 12, 1)
)

# Add relevant research components
proposal_service.add_note_to_workspace(workspace_id, note_id)
proposal_service.add_question_to_workspace(workspace_id, question_id)

# Create the proposal
proposal_id = proposal_service.create_proposal(
    title="Improving Memory Consolidation in Older Adults Through Sleep Interventions",
    funding_agency="National Institute on Aging",
    submission_deadline=datetime(2023, 12, 1)
)

# Link the workspace to the proposal
proposal_service.link_workspace_to_proposal(workspace_id, proposal_id)

# Add a section
proposal_service.add_section(
    proposal_id=proposal_id,
    section_name="specific_aims",
    title="Specific Aims",
    content="1. To characterize the relationship between sleep architecture and memory..."
)
```

## Running Tests

The project includes comprehensive unit tests, integration tests, and performance tests to ensure functionality and meet performance requirements.

```bash
# Install test dependencies
uv add pytest pytest-json-report

# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/performance/

# Generate a JSON report
uv run pytest --json-report --json-report-file=pytest_results.json
```

## Project Structure

```
academic_knowledge_vault/
├── models/             # Data models
│   ├── base.py         # Base models and types
│   ├── note.py         # Note models
│   ├── citation.py     # Citation models
│   ├── ...
├── storage/            # Storage implementations
│   ├── base.py         # Storage interfaces
│   ├── note_storage.py # Note storage
│   ├── ...
├── services/           # Business logic
│   ├── note_management/       # Note management services
│   ├── citation_management/   # Citation management services
│   ├── ...
├── utils/              # Utility functions
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
├── performance/        # Performance tests
```

## Key Features

### Citation-aware Note Linking

The system automatically extracts citation keys (like `@smith2020` or `[@jones2021]`) from your notes and connects them to the corresponding references in your citation database.

### Research Question Framework

Track your research questions, hypotheses, and the evidence that supports or contradicts them. The system calculates evidence strength scores to help you evaluate your hypotheses.

### Grant Proposal Workspaces

Create dedicated workspaces for grant proposals where you can collect relevant notes, citations, research questions, and experiments. The system helps you organize these materials and develop your proposal sections.

### Experiment Management

Create structured templates for your experiments to ensure consistent metadata collection and reproducibility. Link experimental results directly to research questions and hypotheses.

### Knowledge Discovery

The system helps identify potential connections between seemingly disconnected research elements, suggests related materials, and visualizes knowledge gaps and opportunities.

## Performance Benchmarks

- Search and retrieval operations complete in under 500ms for databases with 10,000+ notes
- Index updates after note modifications complete within 2 seconds
- Full-text search across all content returns results in under 1 second
- Citation graph generation handles at least 5,000 interconnected citations
- Bulk operations process at least 50 items per second