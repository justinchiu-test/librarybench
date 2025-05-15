# Unified Personal Knowledge Management Libraries

## Overview
This is a unified implementation of personal knowledge management functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `productmind` - Product manager persona implementation
- `researchbrain` - Academic researcher persona implementation

## Architecture
The unified library follows a modular architecture:

- **Core Components**:
  - Base models for knowledge nodes
  - Storage system for persistence
  - Knowledge graph for representing relationships
  - Search capabilities for accessing information

- **Common Interfaces**:
  - `KnowledgeNode` - Base class for all knowledge objects
  - `BaseStorage` - Interface for data persistence
  - `KnowledgeBase` - Interface for knowledge management
  - Utility functions for common operations

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
import productmind 
import researchbrain

# Import from common package (for shared functionality)
from common.core import models, storage, knowledge
from common.utils import search, conversion
```

### Creating and Managing Knowledge Nodes

```python
from common.core.models import KnowledgeNode
from common.core.storage import LocalStorage
from common.core.knowledge import StandardKnowledgeBase

# Initialize the knowledge management system
storage = LocalStorage("./data")
kb = StandardKnowledgeBase(storage)

# Create and manage knowledge nodes
node = KnowledgeNode(title="Example Note", content="This is a test note")
node_id = kb.add_node(node)
retrieved_node = kb.get_node(node_id)
```

## Testing
Tests are preserved for each persona implementation:

```bash
cd tests
pytest
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Project Structure

```
./
├── common/                        # Common functionality across all implementations
│   ├── core/                      # Core data structures and algorithms
│   │   ├── models.py              # Base knowledge node models
│   │   ├── storage.py             # Storage interface and implementation
│   │   └── knowledge.py           # Knowledge base interface and implementation
│   └── utils/                     # Utility functions
│       ├── conversion.py          # Data conversion utilities
│       ├── file_ops.py            # File operation utilities
│       └── search.py              # Search utilities
├── productmind/                   # Product manager persona implementation
├── researchbrain/                 # Academic researcher persona implementation
├── tests/                         # Tests directory
│   ├── product_manager/           # Tests for product manager persona
│   └── academic_researcher/       # Tests for academic researcher persona
├── PLAN.md                        # Architecture and design plan
├── README.md                      # Project documentation
├── pyproject.toml                 # Project configuration
└── setup.py                       # Installation script
```