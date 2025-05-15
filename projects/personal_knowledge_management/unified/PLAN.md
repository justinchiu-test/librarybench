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

The unified library will be organized into the following core components:

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

### 4. Search Module (`common.core.search`)
- Search interfaces and implementations
- Index management
- Query capabilities

### 5. Utilities Module (`common.utils`)
- Common utility functions
- Type conversions
- ID generation
- Path management

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

## 6. Migration Strategy

### Phase 1: Core Library Implementation
1. Implement the common core components
2. Write comprehensive tests for the core library
3. Ensure broad coverage of common functionality

### Phase 2: Productmind Migration
1. Adapt Productmind models to use the common base models
2. Refactor Productmind to use the common storage system
3. Migrate Productmind's knowledge management logic to use the common library
4. Run all Productmind tests to ensure functionality is preserved

### Phase 3: Researchbrain Migration
1. Adapt Researchbrain models to use the common base models
2. Refactor Researchbrain to use the common storage system
3. Migrate Researchbrain's knowledge management logic to use the common library
4. Run all Researchbrain tests to ensure functionality is preserved

### Phase 4: Integration and Optimization
1. Refine the common library based on lessons learned
2. Optimize performance of shared components
3. Consolidate any remaining duplicate code
4. Ensure all tests pass for both personas

## 7. Implementation Details

### Models Implementation

The base model will provide common fields and methods:

```python
class KnowledgeNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: Set[str] = Field(default_factory=set)
    
    def update(self) -> None:
        self.updated_at = datetime.now()
```

Domain-specific models can inherit from this base:

```python
class Citation(KnowledgeNode):
    title: str
    authors: List[str]
    year: Optional[int] = None
    # ... other fields
```

### Storage Implementation

The storage system will handle persistence with an abstract interface:

```python
class BaseStorage(ABC):
    @abstractmethod
    def save(self, item: T) -> None: ...
    
    @abstractmethod
    def get(self, model_type: Type[T], item_id: UUID) -> Optional[T]: ...
    
    # ... other methods
```

With a file system implementation:

```python
class LocalStorage(BaseStorage):
    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path)
        self._ensure_directories()
        self._cache = {}
        
    def save(self, item: T) -> None:
        # Implementation details
        pass
        
    # ... other methods
```

### Knowledge Graph Implementation

The knowledge graph will manage relationships between objects:

```python
class KnowledgeGraph:
    def __init__(self):
        self._graph = nx.DiGraph()
        
    def add_node(self, node_id: str, **attrs):
        self._graph.add_node(node_id, **attrs)
        
    def add_edge(self, source_id: str, target_id: str, **attrs):
        self._graph.add_edge(source_id, target_id, **attrs)
        
    # ... other methods
```

### Search Implementation

The search system will provide text search capabilities:

```python
class SearchIndex:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self._indexes = {}
        
    def build_index(self, model_type: Type[T], fields: List[str]):
        # Implementation details
        pass
        
    def search(self, model_type: Type[T], query: str, fields: List[str]) -> List[UUID]:
        # Implementation details
        pass
```

## 8. Refactoring Approach

### For Productmind:
1. Update model definitions to inherit from common base models
2. Replace Productmind storage with common storage
3. Refactor Productmind's core classes to use the common knowledge base
4. Map Productmind-specific operations to common interfaces

### For Researchbrain:
1. Update model definitions to inherit from common base models
2. Replace Researchbrain storage with common storage
3. Refactor Researchbrain's core classes to use the common knowledge base
4. Map Researchbrain-specific operations to common interfaces

## 9. Testing Strategy

1. Implement unit tests for all common components
2. Ensure the common library passes all tests in isolation
3. Run persona-specific tests using the common library
4. Fix any integration issues
5. Ensure performance meets or exceeds original implementations

## 10. Schedule and Milestones

### Milestone 1: Core Library Implementation
- Common models
- Storage system
- Knowledge graph
- Search capabilities

### Milestone 2: Productmind Migration
- Adapter models
- Storage migration
- Core functionality migration
- Testing and validation

### Milestone 3: Researchbrain Migration
- Adapter models
- Storage migration
- Core functionality migration
- Testing and validation

### Milestone 4: Final Integration and Testing
- Performance optimization
- Final testing
- Documentation updates

## 11. Risks and Mitigations

### Risk: Incompatible design patterns
- Mitigation: Use adapter patterns to bridge differences

### Risk: Performance degradation
- Mitigation: Implement caching and optimization in the common library

### Risk: Test failures
- Mitigation: Incremental migration and frequent testing

### Risk: Overgeneralization leads to complexity
- Mitigation: Focus on common patterns first, then add abstraction only where needed

## 12. Dependencies

- Pydantic: For data modeling
- NetworkX: For knowledge graph representation
- Python standard library: For core functionality