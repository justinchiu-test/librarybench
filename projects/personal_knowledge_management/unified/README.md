# Unified Personal Knowledge Management System

## Overview
This is a unified implementation of personal knowledge management functionality that provides a common foundation while preserving the original package interfaces for multiple persona implementations:

- `common` - Shared core functionality for all implementations
- `productmind` - Specialized tools for product managers
- `researchbrain` - Specialized tools for academic researchers

## Architecture

The system follows a modular architecture with shared components:

- **Core Components**:
  - **Models**: Base classes for all knowledge entities (KnowledgeNode, Relation)
  - **Storage**: File-based persistence with caching and search indexing
  - **Knowledge Graph**: Representation of relationships between knowledge entities
  - **Utilities**: Common functions for conversion, file operations, and search

- **Extension Points**:
  - Domain-specific node types that inherit from common base classes
  - Specialized knowledge operations for different personas
  - Custom relationship types for domain-specific connections

## Installation

Install the library in development mode:

```bash
pip install -e .
```

## Usage

### Common Library

```python
from common.core.models import KnowledgeNode
from common.core.storage import LocalStorage
from common.core.knowledge import StandardKnowledgeBase

# Initialize storage and knowledge base
storage = LocalStorage("./data")
kb = StandardKnowledgeBase(storage)

# Create and manage nodes
node = KnowledgeNode(title="Example Note", content="Test content")
node_id = kb.add_node(node)
retrieved_node = kb.get_node(node_id)

# Create relationships
kb.link_nodes(node_id, another_node_id, "references")

# Search
results = kb.search("test", node_types=[NoteType])
```

### ResearchBrain Usage

```python
from researchbrain.core.brain import ResearchBrain
from researchbrain.core.models import Note, Citation

# Initialize the research brain
rb = ResearchBrain("./research_data")

# Create notes and citations
note_id = rb.create_note("Research Idea", "This is a promising direction...")
citation_id = rb.create_citation("Deep Learning", ["LeCun", "Bengio", "Hinton"])

# Link notes and papers
rb.link_note_to_paper(note_id, citation_id)

# Create research questions and experiments
rb.create_research_question("How does attention affect performance?")
rb.create_experiment("Attention Study", "Testing effects of visual cues...")
```

### ProductMind Usage

```python
from productmind.feedback_analysis.engine import FeedbackAnalysisEngine
from productmind.models import Feedback, SourceType

# Initialize feedback analysis engine
engine = FeedbackAnalysisEngine("./product_data")

# Add and analyze feedback
feedback = Feedback(
    content="The search feature is difficult to use",
    source=SourceType.APP_REVIEW
)
engine.add_feedback(feedback)
engine.analyze_sentiment([feedback])

# Process feedback
clusters = engine.cluster_feedback()
themes = engine.extract_themes()

# Detect trends
trends = engine.detect_trends(timeframe="week", min_growth_rate=1.5)
```

## Project Structure

```
./
├── common/                        # Common functionality across all implementations
│   ├── core/                      # Core data structures and algorithms
│   │   ├── __init__.py
│   │   ├── knowledge.py           # Knowledge graph and base classes
│   │   ├── models.py              # Shared data models
│   │   └── storage.py             # Storage system
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── conversion.py          # Data format conversion
│       ├── file_ops.py            # File operations
│       └── search.py              # Search utilities
├── productmind/                   # Product manager implementation
│   ├── __init__.py
│   ├── models.py                  # Product-specific models
│   ├── competitive_analysis/      # Competitive analysis tools
│   ├── decision_registry/         # Decision documentation
│   ├── feedback_analysis/         # User feedback processing
│   ├── prioritization/            # Feature prioritization
│   └── stakeholder_insights/      # Stakeholder management
├── researchbrain/                 # Academic researcher implementation
│   ├── __init__.py
│   ├── __main__.py                # Entry point
│   ├── cli.py                     # Command-line interface
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── brain.py               # Main orchestration class
│   │   ├── models.py              # Research-specific models
│   │   └── storage.py             # Research data storage
│   ├── citations/                 # Citation management
│   ├── experiments/               # Experiment templates
│   └── grants/                    # Grant proposal tools
├── tests/                         # Tests for all implementations
│   ├── academic_researcher/       # ResearchBrain tests
│   └── product_manager/           # ProductMind tests
├── PLAN.md                        # Architecture and design plan
├── README.md                      # Project documentation
├── conftest.py                    # Pytest configuration
├── pyproject.toml                 # Project configuration
└── setup.py                       # Installation script
```

## Testing

Run all tests with:

```bash
pytest tests/
```

Or test a specific persona:

```bash
pytest tests/academic_researcher/
pytest tests/product_manager/
```

Generate a test report required for evaluation:

```bash
pytest tests/ --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Key Benefits

1. **Code Reuse**: Common functionality shared across implementations
2. **Modular Design**: Clear separation of concerns
3. **Extensibility**: Easy to add new persona-specific features
4. **Standardized Interfaces**: Consistent APIs across implementations
5. **Reduced Duplication**: Shared core components eliminate redundancy
6. **Improved Maintainability**: Centralized updates to common code