# Architecture and Design Plan for Unified Personal Knowledge Management Library

## Overview
This directory contains a unified implementation of personal knowledge management functionality
that preserves the original package names from the following persona implementations:

- personal_knowledge_management_product_manager (productmind)
- personal_knowledge_management_academic_researcher (researchbrain)

## Directory Structure
```
unified/
├── common/          # Common functionality across all implementations
│   ├── core/        # Core data structures and algorithms
│   └── utils/       # Utility functions and helpers
├── productmind/     # Product manager persona implementation
├── researchbrain/   # Academic researcher persona implementation
├── tests/
│   ├── product_manager/   # Tests for product manager persona
│   └── academic_researcher/  # Tests for academic researcher persona
├── pyproject.toml
└── setup.py
```

## 1. Analysis of Common Patterns

After analyzing both the `productmind` and `researchbrain` implementations, several common patterns have been identified:

### Common Data Structures
- Both implementations use Pydantic `BaseModel` for data models
- Both have core objects with unique identifiers (UUID)
- Both implement timestamp tracking (created_at, updated_at)
- Both use collections of related objects with references between them
- Both use tags for categorization

### Common Functionality
- Storage and retrieval of objects (filesystem-based storage)
- Object relationship management (referencing between objects)
- Serialization/deserialization to disk (YAML/JSON)
- Search capabilities (full-text search)
- Cache management for performance
- Query filtering by attributes

### Common Design Patterns
- Repository pattern for data access
- Factory methods for object creation
- Knowledge graph representation of relationships between entities
- UUID-based references between objects

## 2. Core Components and Responsibilities

The unified library is organized into the following core components:

### 1. Models Module (`common.core.models`)
- Base model classes for all knowledge objects
- Common fields, validators, and behaviors
- Extensible through inheritance for persona-specific models

### 2. Storage Module (`common.core.storage`)
- Abstract storage interface (BaseStorage)
- File system implementation (LocalStorage)
- Operations for CRUD, search, and query
- Serialization/deserialization utilities
- Cache management

### 3. Knowledge Management Module (`common.core.knowledge`)
- Core functionality for managing knowledge objects
- Relationship management between objects
- Graph representation of knowledge relationships
- Traversal and query capabilities

### 4. Utilities Module (`common.utils`)
- Common utility functions
- Type conversions
- File operations
- Search helpers

## 3. Interface Definitions and Abstractions

### BaseModel Interface
```python
class KnowledgeNode(BaseModel):
    """Base class for all knowledge nodes in the system."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def update(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
```

### Storage Interface
```python
class BaseStorage(ABC):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    def save(self, item: T) -> None:
        """Save an item to storage."""
        pass
    
    @abstractmethod
    def get(self, model_type: Type[T], item_id: UUID) -> Optional[T]:
        """Retrieve an item by ID."""
        pass
    
    @abstractmethod
    def delete(self, model_type: Type[T], item_id: UUID) -> bool:
        """Delete an item by ID."""
        pass
    
    @abstractmethod
    def list_all(self, model_type: Type[T]) -> List[T]:
        """List all items of a specific type."""
        pass
    
    @abstractmethod
    def query(self, model_type: Type[T], **filters) -> List[T]:
        """Query items of a specific type with filters."""
        pass
    
    @abstractmethod
    def search_text(self, model_type: Type[T], search_text: str, fields: List[str]) -> List[T]:
        """Search for items containing specific text in certain fields."""
        pass
```

### Knowledge Management Interface
```python
class KnowledgeBase(ABC):
    """Abstract base class for knowledge management system."""
    
    @abstractmethod
    def __init__(self, storage: BaseStorage):
        """Initialize with a storage implementation."""
        pass
    
    @abstractmethod
    def add_node(self, node: KnowledgeNode) -> UUID:
        """Add a knowledge node to the system."""
        pass
    
    @abstractmethod
    def get_node(self, node_id: UUID) -> Optional[KnowledgeNode]:
        """Get a knowledge node by ID."""
        pass
    
    @abstractmethod
    def update_node(self, node: KnowledgeNode) -> bool:
        """Update a knowledge node."""
        pass
    
    @abstractmethod
    def delete_node(self, node_id: UUID) -> bool:
        """Delete a knowledge node."""
        pass
    
    @abstractmethod
    def link_nodes(self, source_id: UUID, target_id: UUID, relation_type: str) -> bool:
        """Create a relationship between two nodes."""
        pass
    
    @abstractmethod
    def get_related_nodes(self, node_id: UUID, relation_types: Optional[List[str]] = None) -> Dict[str, List[Any]]:
        """Get nodes related to a specific knowledge node."""
        pass
    
    @abstractmethod
    def search(self, query: str, node_types: Optional[List[str]] = None) -> Dict[str, List[Any]]:
        """Search for knowledge nodes containing a specific text."""
        pass
```

## 4. Extension Points for Persona-Specific Functionality

### 1. Model Extensions
- Persona-specific models can inherit from common base models
- Custom fields and behaviors can be added
- Domain-specific validation logic can be implemented

### 2. Storage Extensions
- Custom serialization formats
- Specialized indexing for domain-specific search
- Additional persistence mechanisms

### 3. Knowledge Graph Extensions
- Domain-specific relationship types
- Custom traversal and query algorithms
- Specialized visualization methods

### 4. Search Extensions
- Domain-specific search algorithms
- Custom relevance scoring
- Specialized indexing strategies

## 5. Component Relationships

```
+----------------+     +-----------------+
|                |     |                 |
| KnowledgeBase  +---->+   BaseStorage   |
|                |     |                 |
+-------+--------+     +--------+--------+
        |                       |
        |                       |
        v                       v
+-------+--------+     +--------+--------+
|                |     |                 |
|  Knowledge     |     |  LocalStorage   |
|  Graph         |     |                 |
|                |     |                 |
+----------------+     +-----------------+
        ^                       ^
        |                       |
        |                       |
+-------+--------+     +--------+--------+
|                |     |                 |
| KnowledgeNode  +---->+  Serialization  |
|                |     |  Utilities      |
+----------------+     +-----------------+
```

## 6. Implementation Status and Remaining Migration

### Current Status:
1. ✅ Core Components in `common/` have been implemented with:
   - Base models (KnowledgeNode) in `common.core.models`
   - Storage system in `common.core.storage`
   - Knowledge Graph in `common.core.knowledge`
   - Utilities in `common.utils`

2. ✅ ProductMind has been migrated to use the common library:
   - Models inherit from common base models
   - Uses common storage system
   - Uses common knowledge graph

3. ❌ ResearchBrain still needs migration:
   - Currently uses custom models
   - Has custom storage implementation
   - Uses custom knowledge graph implementation

### ResearchBrain Migration Plan:

#### 1. Model Migration
- Refactor `researchbrain.core.models` to inherit from `common.core.models.KnowledgeNode`
- Preserve all existing fields and validation logic
- Standardize common fields (id, created_at, updated_at, tags)

#### 2. Storage Migration
- Replace `researchbrain.core.storage.LocalStorage` with `common.core.storage.LocalStorage`
- Adapt serialization/deserialization logic to maintain backward compatibility
- Update all storage-related calls in the codebase

#### 3. Knowledge Graph Migration
- Replace `researchbrain.core.brain._knowledge_graph` with `common.core.knowledge.KnowledgeGraph`
- Update graph building and traversal logic
- Preserve specialized relationship types and edge attributes

#### 4. ResearchBrain Class Refactoring
- Refactor `ResearchBrain` class to use common components
- Adapt all methods to use the common interfaces
- Preserve all existing functionality and behavior

## 7. Detailed Migration Steps for ResearchBrain

### Phase 1: Model Migration

1. Update all models in `researchbrain.core.models` to inherit from `common.core.models.KnowledgeNode`
2. Update imports to use common enums where applicable
3. Ensure backward compatibility with existing code
4. Create adapter models where necessary for special cases

### Phase 2: Storage Migration

1. Replace `researchbrain.core.storage.LocalStorage` with `common.core.storage.LocalStorage`
2. Update all imports and references in `researchbrain.core.brain`
3. Adapt directory structure to match common storage patterns
4. Update serialization/deserialization logic for compatibility

### Phase 3: Knowledge Graph Migration

1. Refactor `ResearchBrain._build_knowledge_graph()` to use `common.core.knowledge.KnowledgeGraph`
2. Update all graph operations in `ResearchBrain` methods
3. Preserve specialized relationship types and attributes
4. Implement any necessary adapter methods

### Phase 4: Testing and Validation

1. Run all ResearchBrain tests to verify functionality
2. Fix any integration issues
3. Refine common components if needed
4. Ensure performance meets or exceeds original implementation

## 8. Testing Strategy

1. Unit test all common components
2. Integration test with both persona implementations
3. Use existing tests to verify preserved functionality
4. Perform performance benchmarks
5. Run all tests for both personas to ensure compatibility

## 9. Dependencies

- Pydantic: For data modeling
- NetworkX: For knowledge graph representation
- Python standard library: For core functionality

## 10. Risks and Mitigations

### Risk: Breaking existing functionality
- Mitigation: Incremental migration with continuous testing

### Risk: Performance degradation
- Mitigation: Optimize common components and maintain caching

### Risk: Incompatible data formats
- Mitigation: Implement adapter patterns and migration utilities

### Risk: Test failures
- Mitigation: Address each test failure incrementally, preserving existing behavior